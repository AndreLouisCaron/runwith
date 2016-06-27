# -*- coding: utf-8 -*-


import contextlib
import os
import pytest
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
