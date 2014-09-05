#!/usr/bin/python

import argparse
import datetime
import json
import re
import sys

from calendar_service import CalendarService

from icalendar import Calendar, Event, vDatetime, vText

from logger import Logger

from oauth2client.client import AccessTokenRefreshError

from pytz import reference

logger = Logger()


def list_calendars(service):
    calendars = service.get_calendars()
    for calendar in calendars:
        id = calendar['id']
        summary = calendar['summary']
        print '%s: %s' % (id, summary)


def clear_calendar(service, calendar_id):
    service.clear(calendar_id)


def date_vcal2google(date, tz_diff):
    s = date.to_ical()
    if len(s) == 8:
        return '%s-%s-%s' % (s[0:4], s[4:6], s[6:8])

    tz_diff = int(tz_diff)
    if tz_diff < 0:
        tz = '-%02d:%02d' % (tz_diff / 60, tz_diff % 60)
    else:
        tz = '+%02d:%02d' % (tz_diff / 60, tz_diff % 60)
    return '%s-%s-%sT%s:%s:%s%s' % (s[0:4], s[4:6], s[6:8],
                                    s[9:11], s[11:13], s[13:15],
                                    tz)


def get_start(event):
    if 'dateTime' in event['start']:
        return event['start']['dateTime']
    else:
        return event['start']['date']


def find_event(events, event_id, show_deleted=False):
    for event in events:
        if not show_deleted and event['status'] == 'cancelled':
            continue
        if event['id'] == event_id:
            return event
    return None


def e2s(event):
    return '%s: %s' % (get_start(event), event['summary'])


def print_event(event):
    print json.dumps(event, indent=2, sort_keys=True)


def import_vcalendar(ical, not_before=5, not_after=60, exclude=None,
                     no_attendees=False):
    now = datetime.datetime.now()
    today = now.date()

    localtime = reference.LocalTimezone()
    tz_diff = localtime.utcoffset(now).total_seconds() / 60

    not_before = today - datetime.timedelta(days=not_before)
    not_after = today + datetime.timedelta(days=not_after)

    exclude_regex = []
    for x in exclude:
        exclude_regex.append(re.compile(x))

    vcal = Calendar.from_ical(ical)
    local_events = []
    for event in vcal.subcomponents:
        if not isinstance(event, Event):
            continue
        e = {}
        start_date = None
        end_date = None
        for k, v in event.items():
            if k[0] == 'X' or k in ['CLASS', 'PRIORITY', 'DTSTAMP',
                                    'RESOURCE-ID', 'EXDATE', 'TRANSP']:
                continue
            key = k.lower()
            if k == 'UID':
                key = 'id'
                value = unicode(v).lower().replace('-', '')
            elif k == 'RECURRENCE-ID':
                key = 'recurringEventId'
                value = v.to_ical().lower().replace('-', '')
            elif k == 'RRULE':
                key = 'recurrence'
                value = v.to_ical()
                value = ['RRULE:%s' % value]
            elif k == 'ATTENDEE':
                if no_attendees:
                    continue
                key = 'attendees'
                value = []
                for a in v:
                    if 'mailto:' in a and '@' in a:
                        value.append({'email': unicode(a).split(':')[1]})
            elif k in ['DTSTART', 'DTEND']:
                key = k[2:].lower()
                if k == 'DTSTART':
                    start_date = v.dt
                else:
                    end_date = v.dt
                d = date_vcal2google(v, tz_diff)
                if len(d) > 10:
                    value = {'dateTime': d}
                    tzid = v.params.get('TZID', 'Berlin')
                    if 'Berlin' in tzid or 'W. Europe' in tzid:
                        value['timeZone'] = 'Europe/Zurich'
                else:
                    value = {'date': d}
            elif k == 'ORGANIZER' and 'MAILTO:' in v:
                value = {'email': v.split(':')[1]}
            elif k == 'STATUS':
                value = unicode(v).lower()
            else:
                if isinstance(v, vDatetime):
                    value = v.to_ical()
                elif isinstance(v, vText):
                    value = unicode(v)
                else:
                    value = unicode(v)
            e[key] = value
        if 'recurrence' not in e:
            if start_date and end_date:
                if isinstance(start_date, datetime.datetime):
                    start_date = start_date.date()
                if isinstance(end_date, datetime.datetime):
                    end_date = end_date.date()
                if end_date < not_before or start_date > not_after:
                    # skip non recurring events outside our scope
                    logger.log('skip event outside scope: %s' % e2s(e))
                    continue
            if 'recurringEventId' in e:
                # fake unique id for recurring events' instances
                e['id'] += '000' + e['recurringEventId']
        # add default reminders
        e['reminders'] = {'useDefault': True}
        # rename forwarded events
        if e['summary'].startswith('WG: '):
            e['summary'] = e['summary'].replace('WG: ', '')

        # filter summary
        excluded = False
        for regex in exclude_regex:
            if regex.search(e['summary']):
                logger.log('exclude event: %s' % e2s(e))
                excluded = True
                break
        if excluded:
            continue

        # save event to local cache
        local_events.append(e)
    return local_events


def upload_calendar(calendar_service, ical, calendar_id,
                    not_before=5, not_after=60, exclude=None,
                    no_attendees=False):
    local_events = import_vcalendar(ical, not_before, not_after, exclude,
                                    no_attendees)
    google_events = calendar_service.get_events(calendar_id, True)
    added_events = []

    for event in google_events:
        if event['status'] == 'cancelled':
            # skip already deleted events
            continue
        e = find_event(local_events, event['id'])
        if not e:
            logger.log('delete event: %s' % e2s(event))
            # print_event(event)
            calendar_service.delete_event(calendar_id, event['id'])

    for event in local_events:
        e = find_event(google_events, event['id'], True)
        if not e:
            e = find_event(added_events, event['id'])
        if not e:
            logger.log('add event: %s' % e2s(event))
            # print_event(event)
            calendar_service.add_event(calendar_id, event)
            added_events.append(event)
        elif int(e['sequence']) < int(event['sequence']):
            logger.log('update event: %s' % e2s(event))
            calendar_service.update_event(calendar_id, event)
        elif e['status'] == 'cancelled':
            logger.log('re-add event: %s' % e2s(event))
            event['sequence'] = int(e['sequence']) + 1
            # print 'local:'
            # print_event(event)
            # print 'google:'
            # print_event(e)
            calendar_service.update_event(calendar_id, event)
            added_events.append(event)
        else:
            logger.log('skip event: %s' % (e2s(event)))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Upload vcalendar to Google Calendar')
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Suppress output')
    parser.add_argument('-l', '--list-calendars',
                        action='store_true',
                        help='List Google calendars')
    parser.add_argument('-c', '--calendar',
                        nargs=1,
                        metavar='CALENDAR_ID',
                        help='Google Calendar ID')
    parser.add_argument('--clear',
                        action='store_true',
                        help='Clear calendar')
    parser.add_argument('-b', '--not-before',
                        nargs=1,
                        type=int,
                        default=[5],
                        metavar='N',
                        help='Ignore events N days in past, default: 5')
    parser.add_argument('-a', '--not-after',
                        nargs=1,
                        type=int,
                        default=[60],
                        metavar='N',
                        help='Ignore events N days in future, default: 60')
    parser.add_argument('-x', '--exclude',
                        nargs='*',
                        metavar='REGEX',
                        help='Exclude event by matching the summary')
    parser.add_argument('--no-attendees',
                        action='store_true',
                        help='Don\'t upload attendees')
    parser.add_argument('-u', '--upload',
                        nargs=1,
                        type=argparse.FileType('r'),
                        metavar='FILE',
                        help='Upload ics file')
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()
    return args


def main():
    calendar_service = CalendarService()
    args = parse_args()
    logger.set_quiet(args.quiet)

    try:
        # action: list calendars
        if args.list_calendars:
            list_calendars(calendar_service)
            return

        # select calendar
        if args.calendar:
            calendar_id = args.calendar[0]
        else:
            calendar_id = 'primary'

        # action: clear calendar
        if args.clear:
            clear_calendar(calendar_service, calendar_id)
            return

        # action: upload calendar
        upload_calendar(calendar_service, args.upload[0].read(), calendar_id,
                        args.not_before[0], args.not_after[0],
                        args.exclude, args.no_attendees)
    except AccessTokenRefreshError:
        # The AccessTokenRefreshError exception is raised if the credentials
        # have been revoked by the user or they have expired.
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize')

if __name__ == '__main__':
    main()
