import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def read_upcoming_events():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  output = ""
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "/Users/Tim/Documents/Luna API/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        output = "No upcoming events found."
        return output

    # Prints the start and name of the next 10 events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start)
        output = output + "[Date: " + start + " - " + event["summary"] + "]; "
    print(output)
  except HttpError as error:
        print(f"An error occurred: {error}")
  return output

def add_new_event(date, durartion, title, description):
    start = datetime.datetime.utcnow()

    end = datetime.datetime.utcnow() + datetime.timedelta(hours=durartion)
    start_formatted = start.isoformat() + 'Z'
    end_formatted = end.isoformat() + 'Z'

    event = {
        'name': title,
        'summary': description,
        'start': {
            'dateTime': start_formatted,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': 'Europe/Berlin',
        },
    }
    service = build("calendar", "v3", credentials=Credentials.from_authorized_user_file())
    event = service.events().insert(calendarId='', body=event).execute()
