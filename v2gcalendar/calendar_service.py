__author__ = 'flx'

from apiclient.discovery import build

import httplib2

from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow


# For this example, the client id and client secret are command-line arguments.
client_id = \
    '826222712854-das8sdv4veehjje2o4e45sbvnrd8fi5n.apps.googleusercontent.com'
client_secret = 'CKBI_J4aE7QaEWLTxTyjGF-u'

# The scope URL for read/write access to a user's calendar data
scope = 'https://www.googleapis.com/auth/calendar'

# Create a flow object. This object holds the client_id, client_secret, and
# scope. It assists with OAuth 2.0 steps to get user authorization and
# credentials.
flow = OAuth2WebServerFlow(client_id, client_secret, scope)


class CalendarService:

    def __init__(self):
        self._service = None
        self.init_service()

    def init_service(self):
        if self._service:
            return
        storage = Storage('credentials.dat')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            parser = tools.argparser
            flags = parser.parse_args([])
            credentials = run_flow(flow, storage, flags)
        http = httplib2.Http()
        http = credentials.authorize(http)
        self._service = build('calendar', 'v3', http=http)

    def get_calendars(self):
        result = []
        request = self._service.calendarList().list()
        while request:
            response = request.execute()
            for calendar in response.get('items', []):
                result.append(calendar)
            request = self._service.calendarList().list_next(request, response)
        return result

    def find_calendar(self, name):
        calendars = self.get_calendars()
        for calendar in calendars:
            if calendar['summary'] == name:
                return calendar['id']

    def clear(self, calendar_id):
        request = self._service.calendars().clear(calendarId=calendar_id)
        result = request.execute()
        return result

    def get_events(self, calendar_id, show_deleted=False):
        results = []
        request = self._service.events().list(calendarId=calendar_id,
                                              showDeleted=show_deleted)
        while request:
            response = request.execute()
            for event in response.get('items', []):
                results.append(event)
            request = self._service.events().list_next(request, response)
        return results

    def add_event(self, calendar_id, event):
        response = self._service.events().insert(calendarId=calendar_id,
                                                 body=event,
                                                 sendNotifications=False)\
            .execute()
        return response

    def update_event(self, calendar_id, event):
        response = self._service.events().update(calendarId=calendar_id,
                                                 eventId=event['id'],
                                                 body=event,
                                                 sendNotifications=False)\
            .execute()
        return response

    def delete_event(self, calendar_id, event_id):
        response = self._service.events().delete(calendarId=calendar_id,
                                                 eventId=event_id,
                                                 sendNotifications=False)\
            .execute()
        return response
