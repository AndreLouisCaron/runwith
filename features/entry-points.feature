# -*- coding: utf-8 -*-

Feature: entry points

  Scenario: run directly

    When I run `runwith`
    Then I see the CLI usage

  Scenario: run through Python

    When I run `python -m runwith`
    Then I see the CLI usage
