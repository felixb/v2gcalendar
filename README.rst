****************************
vcalendar to Google calendar
****************************

.. image:: https://pypip.in/v/v2gcalendar/badge.png
    :target: https://pypi.python.org/pypi/v2gcalendar/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/v2gcalendar/badge.png
    :target: https://pypi.python.org/pypi/v2gcalendar/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/felixb/v2gcalendar
    :target: https://travis-ci.org/felixb/v2gcalendar
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/felixb/v2gcalendar/badge.png
   :target: https://coveralls.io/r/felixb/v2gcalendar
   :alt: Test coverage

Upload a vcalendar file into your Google Calendar.


Installation
============

Install the v2gcalendar by running::

    pip install v2gcalendar


Usage
=====

The main.py handles the following commands::

    main.py -l, --list-calendars
        List all available calendars

    main.py --clear
        Clear a calendar


    main.py -u, --upload
        Upload a ics file to Google calendar

        The following arguments are supported:

        -b, --not-before
            Ignore events before N days in past
        -a, --not-after
            Ignore events after N days in future
        -x, --exclude
            Ignore events by matching the summary


Common arguments are available::

    -q, --quiet
        Suppress ouput
    -c, --calendar
        Select a calendar by it's id

Project resources
=================

- `Source code <https://github.com/felixb/v2gcalendar>`_
- `Issue tracker <https://github.com/felixb/v2gcalendar/issues>`_
- `Download development snapshot
  <https://github.com/felixb/v2gcalendar/archive/develop.zip>`_


Changelog
=========

v0.0.1 (UNRELEASED)
-------------------

- Initial release
