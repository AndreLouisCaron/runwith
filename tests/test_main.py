# -*- coding: utf-8 -*-


from __future__ import (
    print_function,
    unicode_literals,
)

import hypothesis
import hypothesis.strategies
import mock
import os.path
import pytest

from datetime import timedelta
from hypothesis_regex import regex
from runwith import (
    main,
    __main__,
    timespan,
    SIGKILL,
)

try:
    from shlex import quote
except ImportError:
    from pipes import quote


def unused(*args):
    pass


# Must be imported to be tracked by coverage.
unused(__main__)


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY


def seconds_to_timespan(x):
    y = ''
    weeks, x = divmod(x, WEEK)
    if weeks:
        y += '%dw' % weeks
    days, x = divmod(x, DAY)
    if days:
        y += '%dd' % days
    hours, x = divmod(x, HOUR)
    if hours:
        y += '%dh' % hours
    minutes, x = divmod(x, MINUTE)
    if minutes:
        y += '%dm' % minutes
    seconds, x = divmod(x, SECOND)
    if seconds:
        y += '%ds' % seconds
    if x > 0:
        y += '%dms' % (1000.0 * x)
    return y


@pytest.mark.parametrize('value,expected', [
    ('1w', timedelta(weeks=1)),
    ('7d', timedelta(days=7)),
    ('2h', timedelta(hours=2)),
    ('.1m', timedelta(minutes=.1)),
    ('.7s', timedelta(seconds=.7)),
    ('5m30s', timedelta(minutes=5, seconds=30)),
])
def test_timespan(value, expected):
    assert timespan(value) == expected


@pytest.mark.parametrize('value', [
    '1',
    '123abc',
])
def test_timespan_invalid(value):
    with pytest.raises(ValueError) as exc:
        print(timespan(value))
    assert str(exc.value) == ('Invalid time span "%s".' % value)


def test_run_without_args():
    with mock.patch('subprocess.Popen') as popen:
        with pytest.raises(SystemExit) as exc:
            print(main([]))
        assert exc.value.code == 2
        popen.assert_not_called()


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_implicit_argv(status, command):
    with mock.patch('sys.argv', ['runwith', '--'] + command):
        process = mock.MagicMock()
        process.returncode = status
        process.wait.return_value = process.returncode
        with mock.patch('subprocess.Popen') as popen:
            popen.side_effect = [process]
            assert main() == status
            popen.assert_called_once_with(command)


@hypothesis.given(
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_spawn_failure(command):
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = OSError('unknown program')
        with pytest.raises(SystemExit) as exc:
            print(main(['--'] + command))
        assert exc.value.code == 2
        popen.assert_called_once_with(command)


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_forward_status(status, command):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['--'] + command) == status
        popen.assert_called_once_with(command)


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_redirect_stdin(tempcwd, status, command):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    with open('foo.txt', 'wb') as stream:
        stream.write(b'FOO')
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['-i', 'foo.txt', '--'] + command) == status
        popen.assert_called_once_with(command, stdin=mock.ANY)


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_redirect_stdout(tempcwd, status, command):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['-o', 'foo.txt', '--'] + command) == status
        popen.assert_called_once_with(command, stdout=mock.ANY)
    assert os.path.exists('foo.txt')


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
)
def test_redirect_stderr(tempcwd, status, command):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['-e', 'foo.txt', '--'] + command) == status
        popen.assert_called_once_with(command, stderr=mock.ANY)
    assert os.path.exists('foo.txt')


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
    workdir=regex(r'\w+').map(quote),
)
def test_change_working_directory(tempcwd, status, command, workdir):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['-w', workdir, '--'] + command) == status
        popen.assert_called_once_with(command, cwd=workdir)


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
    timebox=hypothesis.strategies.floats(
        min_value=0.001,  # 1ms
        max_value=31 * DAY,
    ).map(seconds_to_timespan),
)
def test_respect_timebox(status, command, timebox):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.side_effect = [process.returncode]
    with mock.patch('subprocess.Popen') as popen:
        popen.side_effect = [process]
        assert main(['-t', timebox, '--'] + command) == status
        popen.assert_called_once_with(command)
        process.wait.assert_called_once_with()
        process.send_signal.assert_not_called()
        process.terminate.assert_not_called()


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
    timebox=hypothesis.strategies.floats(
        min_value=0.001,  # 1ms
        max_value=31 * DAY,
    ).map(seconds_to_timespan),
)
def test_exceed_timebox(status, command, timebox):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    thread = mock.MagicMock()
    thread.is_alive.side_effect = [True, False]
    thread.join.side_effect = [None, None]
    with mock.patch('threading.Thread') as T:
        T.side_effect = [thread]
        with mock.patch('subprocess.Popen') as P:
            P.side_effect = [process]
            assert main(['-t', timebox, '-g', '2s', '--'] + command) == status
            P.assert_called_once_with(command)
            T.assert_called_once()
            process.send_signal.assert_called_once_with(SIGKILL)
            process.terminate.assert_not_called()


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
    timebox=hypothesis.strategies.floats(
        min_value=0.001,  # 1ms
        max_value=31 * DAY,
    ).map(seconds_to_timespan),
)
def test_exceed_timebox_no_grace_time(status, command, timebox):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    thread = mock.MagicMock()
    thread.is_alive.side_effect = [True, True]
    thread.join.side_effect = [None, None, None]
    with mock.patch('threading.Thread') as T:
        T.side_effect = [thread]
        with mock.patch('subprocess.Popen') as P:
            P.side_effect = [process]
            assert main(['-t', timebox, '--'] + command) == status
            P.assert_called_once_with(command)
            T.assert_called_once()
            process.send_signal.assert_not_called()
            process.terminate.assert_called_once()


@hypothesis.given(
    status=hypothesis.strategies.integers(min_value=-128, max_value=127),
    command=hypothesis.strategies.lists(
        elements=hypothesis.strategies.text(min_size=1),
        min_size=1,
    ),
    timebox=hypothesis.strategies.floats(
        min_value=0.001,  # 1ms
        max_value=31 * DAY,
    ).map(seconds_to_timespan),
)
def test_exceed_timebox_and_grace_time(status, command, timebox):
    process = mock.MagicMock()
    process.returncode = status
    process.wait.return_value = process.returncode
    thread = mock.MagicMock()
    thread.is_alive.side_effect = [True, True]
    thread.join.side_effect = [None, None, None]
    with mock.patch('threading.Thread') as T:
        T.side_effect = [thread]
        with mock.patch('subprocess.Popen') as P:
            P.side_effect = [process]
            assert main(['-t', timebox, '-g', '2s', '--'] + command) == status
            P.assert_called_once_with(command)
            T.assert_called_once()
            process.send_signal.assert_called_once_with(SIGKILL)
            process.terminate.assert_called_once()
