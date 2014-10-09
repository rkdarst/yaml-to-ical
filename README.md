yaml-to-ical
============

Easily convert a calendar marked up in YAML to the iCalendar format.

Usage
-----
```
Usage: bin/convert-yaml [INPUT_FILE]
       bin/convert-yaml [INPUT_FILE] [OUTPUT_FILE]
```

Example Input File
------------------
```YAML
options:
    title: Timetable
    count_in_title: true
    timezone: Europe/London

periods:
    - &term1
      start: 2014-10-01
      end: 2014-12-01
    - &term2
      start: 2015-01-01
      end: 2015-05-01

locations:
    - &loc1
      name: Hall 1
      description: >-
          Hall 1,
          Road Name
          Post Code

events:
    - name: Lecture Name
      description: Topics: A, B, C
      location: *loc1
      periods: [*term1, *term2]
      days: [mo, we, fr]
      repeat: 50
      start_time: 10:00:00
      end_time: 11:00:00
      out_of: 60
      start_at: 3
      meta:
          - attribute: Lecturer
            value: Dr J Smith
      overrides:
          2014-10-10 10:00:00:
              start: 2014-10-11 10:00:00
              end: 2014-10-11 11:00:00
```

Authors
-------
See AUTHORS.

License
-------
See LICENSE.
