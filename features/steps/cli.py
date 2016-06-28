# -*- coding: utf-8 -*-


import timeit
import os
import os.path
import shlex
import subprocess

from behave import (
    given,
    when,
    then,
)


@given('File "{path}" contains "{data}"')
def write(context, path, data):
    with open(path, 'wb') as stream:
        stream.write(data.encode('utf-8'))


@given('Folder "{path}" exists')
def create(context, path):
    os.mkdir(path)


@when('I run `{command}`')
def spawn(context, command):

    # Make sure no process is currently running.
    process = getattr(context, 'process', None)
    if process and process.returncode is None:
        raise Exception('Process already running.')

    # Split the command into a list to avoid running under insecure shell mode.
    command = shlex.split(command)

    print('CWD:', os.getcwd())

    # Start the new process.
    context.environ = {
        k: v for k, v in os.environ.items()
    }
    context.environ['PYTHONUNBUFFERED'] = '1'
    context.command = command
    context.process = subprocess.Popen(
        context.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=context.environ,
    )
    context.reftime = timeit.default_timer()


@then('I see the CLI usage')
def check_usage(context):
    output, _ = context.process.communicate()
    output = output.decode('utf-8').strip()
    status = context.process.wait()
    assert status == 2
    print('OUTPUT: %r' % output)
    assert output.startswith('usage: runwith')


@then('The output contains "{data}"')
def check_output_contains(context, data):
    output, _ = context.process.communicate()
    output = output.decode('utf-8').strip()
    status = context.process.wait()
    print('OUTPUT:', output)
    assert status == 0
    assert data in output


@then('The output ends with "{data}"')
def check_output_ends_with(context, data):
    output, _ = context.process.communicate()
    output = output.decode('utf-8').strip()
    status = context.process.wait()
    if status != 0:
        print('OUTPUT: %r' % output)
    assert status == 0
    assert output.endswith(data)


@then('File "{path}" contains "{data}"')
def check_output_file_contains(context, path, data):
    output, _ = context.process.communicate()
    status = context.process.wait()
    if status != 0:
        print('OUTPUT: %r' % output)
    with open(path, 'rb') as stream:
        output = stream.read().decode('utf-8').strip()
    assert status == 0
    assert data in output


@then('The process ran at most {time} seconds')
def check_elapsed_time_at_most(context, time):

    # Wait until the process completes.
    if context.process.returncode is None:
        output, _ = context.process.communicate()
        status = context.process.wait()
        print('STATUS:', status)
        if status != 0:
            print('OUTPUT: %r' % output)

    # Check elapsed time.
    ref = context.reftime
    now = timeit.default_timer()
    elapsed = (now - ref)
    if elapsed <= float(time):
        print('ELAPSED:', elapsed)
    assert elapsed <= float(time)


@then('The process ran at least {time} seconds')
def check_elapsed_time_at_least(context, time):

    # Wait until the process completes.
    if context.process.returncode is None:
        output, _ = context.process.communicate()
        status = context.process.wait()
        if status != 0:
            print('OUTPUT: %r' % output)

    # Check elapsed time.
    ref = context.reftime
    now = timeit.default_timer()
    elapsed = (now - ref)
    if elapsed <= float(time):
        print('ELAPSED:', elapsed)
    assert elapsed >= float(time)


@given('Fixture file "{path}"')
def write_fixture_file(context, path):
    """Write fixture to disk."""

    print('CWD:', os.getcwd())
    print('FIXTURE:', path)
    with open(path, 'w') as stream:
        stream.write(context.text)
