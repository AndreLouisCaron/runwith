# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import subprocess
import sys


cli = argparse.ArgumentParser('runwith')
cli.add_argument('command', nargs='+')


def main(argv=None):
    """Program entry point."""

    # If we're invoked directly (runwith ...), we'll get None here.
    if argv is None:
        argv = sys.argv[1:]

    # Parse command-line arguments.
    argv = cli.parse_args(argv)

    # Start the child process.
    options = {}
    try:
        process = subprocess.Popen(
            argv.command, **options
        )
    except OSError:
        print('Invalid command %r.' % argv.command)
        sys.exit(2)

    # Wait for the child process to complete.
    status = process.wait()
    assert status is not None

    # Forward exit code.
    return status
