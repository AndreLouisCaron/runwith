# -*- coding: utf-8 -*-

Feature: time box

  Scenario: command completes before deadline
    Given Fixture file "script.py"
      """
      print('START')
      print('DONE')
      """
    When I run `runwith -t 1s -- python script.py`
    Then The process ran at most 1.1 seconds

  Scenario: command exceeds deadline, but completes
    Given Fixture file "script.py"
      """
      print('START')
      import time
      try:
          time.sleep(.2)
      except KeyboardInterrupt:
          print('SIGINT')
      print('DONE')
      """
    When I run `runwith -t .1s -g 1s -- python script.py`
    Then The process ran at least 0.1 seconds
     But The process ran at most 0.5 seconds

  Scenario: command exceeds deadline and is terminated
    Given Fixture file "script.py"
      """
      print('START')
      import time
      import timeit
      now = timeit.default_timer()
      deadline = now + 1.5
      while deadline > now:
          print('SLEEP:', deadline - now)
          try:
              time.sleep(deadline - now)
          except KeyboardInterrupt:
              print('SIGINT')
          now = timeit.default_timer()
          print('LOOP')
      print('DONE')
      """
    When I run `runwith -t .1s -g .1s -- python script.py`
    Then The process ran at least 0.1 seconds
     But The process ran at most 0.3 seconds
