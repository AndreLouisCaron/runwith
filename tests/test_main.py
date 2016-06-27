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

from runwith import main, __main__


def unused(*args):
    pass


# Must be imported to be tracked by coverage.
unused(__main__)


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
