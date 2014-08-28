__author__ = 'flx'

import unittest

from icalendar.prop import vDatetime

from v2gcalendar.main import date_vcal2google, get_start


class MainTest(unittest.TestCase):

    def test_date_vcal2google(self):
        self.assertEqual(
            date_vcal2google(
                vDatetime(vDatetime.from_ical('20140828T120150')), 120),
            '2014-08-28T12:01:50+02:00')

    def test_get_start(self):
        self.assertTrue(get_start({'start': {'dateTime': True}}))
        self.assertTrue(get_start({'start': {'date': True}}))
