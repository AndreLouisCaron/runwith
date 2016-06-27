# -*- coding: utf-8 -*-

Feature: I/O redirection

  Scenario: redirect standard input

    Given File "foo.txt" contains "FOO"
    When I run `runwith -i foo.txt -- python -c 'import sys;  print(sys.stdin.read())'`
    Then The output contains "FOO"

  Scenario: redirect standard output

    When I run `runwith -o foo.txt -- python -c 'import sys;  sys.stdout.write("FOO")'`
    Then File "foo.txt" contains "FOO"

  Scenario: redirect standard error

    When I run `runwith -e foo.txt -- python -c 'import sys;  sys.stderr.write("FOO")'`
    Then File "foo.txt" contains "FOO"
