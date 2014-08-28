__author__ = 'flx'

import unittest

import mock

from v2gcalendar.logger import Logger


class LoggerTest(unittest.TestCase):

    def test_init(self):
        logger = Logger()
        logger.log('foo')

    def test_log(self):
        logger = Logger()
        logger._log = mock.Mock()
        logger.log('foo')
        logger._log.assert_called_once_with('foo')

    def test_quiet(self):
        logger = Logger()
        logger._log = mock.Mock()
        logger.set_quiet(True)
        logger.log('foo')
        self.assertEqual(logger._log.call_count, 0)
