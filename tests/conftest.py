# -*- coding: utf-8 -*-


import contextlib
import mock
import os
import pytest
import sys
import testfixtures


@contextlib.contextmanager
def cwd(path):
    """Context manager to temporarily enter a new working directory."""
    old_cwd = os.getcwd()
    new_cwd = path
    os.chdir(new_cwd)
    try:
        print('CWD:', new_cwd)
        yield
    finally:
        os.chdir(old_cwd)


@pytest.yield_fixture(scope='function')
def tempdir():
    """py.test fixture to create and cleanup a temporary directory."""
    directory = testfixtures.TempDirectory(create=True)
    yield directory
    directory.cleanup()


@pytest.yield_fixture(scope='function')
def tempcwd(tempdir):
    """py.test fixture to create, enter and cleanup a temporary directory."""
    with cwd(tempdir.path):
        yield


@contextlib.contextmanager
def handle_ctrlc(handler):
    """Intercept CTRL-C to replace the system's default behavior.

    On Windows, ``GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)`` sends the CTRL-C
    event to all processes in the group.  When a test sends it to a child
    process, it will also be sent to the current process, which typically stops
    ``py.test`` after the current test.  Using a custom handler allows us to
    suppress the signal in the current process.

    This is not necessary on POSIX systems because ``SIGKILL`` is only sent to
    the target/child process.

    Compatibility: Windows only (not necessary elsewhere).

    """

    from ctypes import WINFUNCTYPE, windll
    from ctypes.wintypes import BOOL, DWORD

    phandler_routine = WINFUNCTYPE(BOOL, DWORD)
    SetConsoleCtrlHandler = windll.kernel32.SetConsoleCtrlHandler
    CTRL_C_EVENT = 0

    # NOTE: for some reason, it seems like this never gets included
    #       in the code coverage report (probably because it's invoked
    #       as a ctypes callback).
    @phandler_routine
    def console_ctrl_handler(event):  # pragma: no cover
        if event == CTRL_C_EVENT:
            handler()
            return 1
        return 0

    if SetConsoleCtrlHandler(console_ctrl_handler, 1) == 0:
        raise WindowsError()
    try:
        yield
    finally:
        if SetConsoleCtrlHandler(console_ctrl_handler, 0) == 0:
            raise WindowsError()


@pytest.yield_fixture(scope='function')
def ignore_ctrlc(tempdir):
    """py.test fixture to ignore CTRL-C events during a test."""

    noop = mock.MagicMock()

    if sys.platform == 'win32':
        with handle_ctrlc(noop):
            yield noop
    else:
        # Nothing to do!
        yield noop
