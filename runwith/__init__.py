# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import datetime
import re
import subprocess
import sys
import threading

try:
    from signal import SIGKILL
except ImportError:
    from signal import CTRL_C_EVENT

try:
    # py3
    from contextlib import ExitStack, closing
except ImportError:
    # py2
    from contextlib2 import ExitStack, closing


def timespan(x):
    pattern = re.compile(
        ''.join((
            r'^',
            '(?:(?P<weeks>\d*\.?\d*)w)?',
            '(?:(?P<days>\d*\.?\d*)d)?',
            '(?:(?P<hours>\d*\.?\d*)h)?',
            '(?:(?P<minutes>\d*\.?\d*)m(?!s))?',
            '(?:(?P<seconds>\d*\.?\d*)s)?',
            '(?:(?P<milliseconds>\d*\.?\d*)ms)?',
            r'$',
        )),
    )
    match = re.match(pattern, x)
    if not match:
        raise ValueError('Invalid time span "%s".' % x)
    match = {
        k: float(v)
        for k, v in match.groupdict().items() if v is not None
    }
    return datetime.timedelta(**match)


cli = argparse.ArgumentParser('runwith')
cli.add_argument('-i', '--stdin', type=argparse.FileType('r'))
cli.add_argument('-o', '--stdout', type=argparse.FileType('w'))
cli.add_argument('-e', '--stderr', type=argparse.FileType('w'))
cli.add_argument('-w', '--cwd')
cli.add_argument('-t', '--time-limit', type=timespan)
cli.add_argument('-g', '--grace-time', type=timespan)
cli.add_argument('command', nargs='+')


def main(argv=None):
    """Program entry point."""

    # If we're invoked directly (runwith ...), we'll get None here.
    if argv is None:
        argv = sys.argv[1:]

    # Parse command-line arguments.
    argv = cli.parse_args(argv)

    # Make sure we close the handles.
    with ExitStack() as stack:
        for k in ('stdin', 'stdout', 'stderr'):
            stream = getattr(argv, k, None)
            if stream:
                stack.enter_context(closing(stream))

    # Translate CLI arguments to Popen options.
    options = {}
    for k in ('stdin', 'stdout', 'stderr', 'cwd'):
        v = getattr(argv, k, None)
        if v:
            options[k] = v

    # Start the child process.
    try:
        process = subprocess.Popen(
            argv.command, **options
        )
    except OSError:
        print('Invalid command %r.' % argv.command)
        sys.exit(2)

    # Wait for the child process to complete.
    #
    # NOTE: there is no timeout on `process.wait()` so we use the timeout on a
    #       thread as a workaround.
    thread = threading.Thread(target=process.wait)
    thread.start()
    if argv.time_limit is None:
        thread.join()
    else:
        thread.join(min(.05, argv.time_limit.total_seconds()))
    if thread.is_alive() and argv.grace_time:
        if sys.platform == 'win32':
            from ctypes import windll
            GenerateConsoleCtrlEvent = windll.kernel32.GenerateConsoleCtrlEvent
            if GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0) == 0:
                raise WindowsError()
        else:
            process.send_signal(SIGKILL)
        thread.join(argv.grace_time.total_seconds())
    if thread.is_alive():
        process.terminate()
        thread.join()
    status = process.returncode
    assert status is not None

    # Forward exit code.
    return status
