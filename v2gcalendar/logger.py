__author__ = 'flx'


class Logger:

    def __init__(self):
        self._quiet = False

    def set_quiet(self, quiet):
        self._quiet = quiet

    def log(self, message):
        if not self._quiet:
            self._log(message)

    def _log(self, message):
        print message
