# -*- coding: utf-8 -*-


import shlex
import subprocess

from behave import (
    when,
    then,
)


@when('I run `{command}`')
def spawn(context, command):

    # Make sure no process is currently running.
    process = getattr(context, 'process', None)
    if process and process.returncode is None:
        raise Exception('Process already running.')

    # Split the command into a list to avoid running under insecure shell mode.
    command = shlex.split(command)

    # Start the new process.
    context.command = command
    context.process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


@then('I see the CLI usage')
def check_usage(context):
    output, _ = context.process.communicate()
    output = output.decode('utf-8').strip()
    status = context.process.wait()
    assert status == 2
    print('OUTPUT: %r' % output)
    assert output.startswith('usage: runwith')
