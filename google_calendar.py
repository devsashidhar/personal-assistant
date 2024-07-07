from __future__ import print_function
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:60440/'
            creds = flow.run_local_server(port=60440)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(service, summary, start_time, end_time, location=None, description=None, attendees=None):
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
        'attendees': [{'email': attendee} for attendee in attendees] if attendees else [],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event

def list_upcoming_events(service, max_results=10):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    future = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + 'Z'
    print(f"Current time: {now}")
    print(f"Future time (30 days ahead): {future}")
    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=future, maxResults=max_results, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    else:
        print(f"Found {len(events)} upcoming events.")
        for i, event in enumerate(events):
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{i+1}. {start} - {event['summary']} (ID: {event['id']})")
    return events

def update_event(service, event_id, summary=None, start_time=None, end_time=None, location=None, description=None, attendees=None):
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    if summary:
        event['summary'] = summary
    if start_time:
        event['start']['dateTime'] = start_time
        event['start']['timeZone'] = 'America/New_York'
    if end_time:
        event['end']['dateTime'] = end_time
        event['end']['timeZone'] = 'America/New_York'
    if location:
        event['location'] = location
    if description:
        event['description'] = description
    if attendees:
        event['attendees'] = [{'email': attendee} for attendee in attendees]

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print(f"Event updated: {updated_event.get('htmlLink')}")
    return updated_event

def delete_event(service, event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print(f"Event with ID {event_id} deleted.")

if __name__ == '__main__':
    service = authenticate_google_calendar()
    
    # List upcoming events to get the event ID
    events = list_upcoming_events(service)
    
    if events:
        choice = int(input("Enter the number of the event you want to update/delete: ")) - 1
        selected_event_id = events[choice]['id']
        
        # Example: Updating the selected event
        update_event(service, selected_event_id, summary='Updated Event', start_time='2024-07-07T12:00:00-04:00', end_time='2024-07-07T13:00:00-04:00')
        
        # Example: Deleting the selected event
        delete_event(service, selected_event_id)
