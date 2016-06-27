# -*- coding: utf-8 -*-

Feature: I/O redirection

  Scenario: redirect input

    Given File "foo.txt" contains "FOO"
    When I run `runwith -i foo.txt -- python -c 'import sys;  print(sys.stdin.read())'`
    Then The output contains "FOO"
