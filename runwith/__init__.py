# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import subprocess
import sys


cli = argparse.ArgumentParser('runwith')
cli.add_argument('-i', '--stdin', type=argparse.FileType('r'))
cli.add_argument('-o', '--stdout', type=argparse.FileType('w'))
cli.add_argument('-e', '--stderr', type=argparse.FileType('w'))
cli.add_argument('-w', '--cwd')
cli.add_argument('command', nargs='+')


def main(argv=None):
    """Program entry point."""

    # If we're invoked directly (runwith ...), we'll get None here.
    if argv is None:
        argv = sys.argv[1:]

    # Parse command-line arguments.
    argv = cli.parse_args(argv)

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
    status = process.wait()
    assert status is not None

    # Forward exit code.
    return status
