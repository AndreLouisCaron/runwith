# -*- coding: utf-8 -*-

Feature: working directory

  Scenario: execute command in another working directory

    Given Folder "foo" exists
    When I run `runwith -w foo -- python -c 'import os;  print(os.getcwd())'`
    Then The output ends with "/foo"
