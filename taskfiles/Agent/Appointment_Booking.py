
from typing import Dict
from taskfiles.Shared import State
from dateutil import parser
from datetime import datetime, timedelta
from langchain.tools import tool
import re
import pytz
from typing_extensions import TypedDict, Literal, Annotated
from langgraph.types import Command
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage




# ========== Setup calender ==========
from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.utils import (
    build_resource_service,
    get_google_credentials,
)

credentials = get_google_credentials(
    token_file="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
    client_secrets_file="credentials.json",
)

api_resource = build_resource_service(credentials=credentials)
toolkit = CalendarToolkit(api_resource=api_resource)






# ========== Calender Events ==========
@tool
def book_event_by_time(state: State, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Books a calendar event using natural language like 'Book at 5pm today for John Doe, john@example.com'. Requires name and email."""
    try:
        booking_time = state["booking_time_date"]
        
        name = state["name"]
        email = state["email"]


        if not booking_time:
            return Command(update={
                "messages": [ToolMessage(
                    content=" Sorry, I couldn't find a date or time in your message. Please try again with something like 'Book at 5pm today'.",
                    name="book_event_by_time",
                    tool_call_id=tool_call_id)]
            })

        try:
            target_time = parser.parse(booking_time, fuzzy=True)
        except ValueError:
            return Command(update={
                "messages": [ToolMessage(
                    content="Sorry, I couldn't find a date or time in your message. Please try again with something like 'Book at 5pm today'.",
                    name="book_event_by_time",
                    tool_call_id=tool_call_id)]
            })


        if not name or not email:
            return Command(update={
                "messages": [ToolMessage(
                    content="Please provide both your *full name* and *email address* to book the appointment.",
                    name="book_event_by_time",
                    tool_call_id=tool_call_id)]
            })

        start_dt = target_time.replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC)
        end_dt = (target_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC)

        start = start_dt.isoformat()
        end = end_dt.isoformat()

        events_result = api_resource.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        if events:
            for evt in events:
                attendees = evt.get('attendees', [])
                emails = [a.get('email') for a in attendees if a.get('email')]
                if email in emails:
                    return Command(update={
                        "messages": [ToolMessage(
                            content=f"You've already booked this slot at {start_dt.strftime('%I:%M %p on %A, %B %d')}.",
                            name="book_event_by_time",
                            tool_call_id=tool_call_id)]
                    })
                else:
                    booked_by = evt.get('summary', 'someone else')
                    return Command(update={
                        "messages": [ToolMessage(
                            content=f"That time slot is already booked by {booked_by}. Please choose another time.",
                            name="book_event_by_time",
                            tool_call_id=tool_call_id)]
                    })

        event = {
            'summary': f"Appointment with {name}",
            'description': f"Booked by {name}. at: {booking_time}",
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'},
            'attendees': [{'email': email}],
        }

        created_event = api_resource.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

        return Command(update={
            "messages": [ToolMessage(
                content=f"Appointment booked for {name} at {start_dt.strftime('%I:%M %p on %A, %B %d')}.",
                name="book_event_by_time",
                tool_call_id=tool_call_id)]
        })

    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f"Error: {str(e)}",
                name="book_event_by_time",
                tool_call_id=tool_call_id)]
        })

        
@tool
def cancel_event_by_time(state: State, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Cancel a calendar event based on natural language like 'Cancel my 6pm today booking'."""
    try:

        cancel_time = state["booking_time_date"]
        email = state["email"]

        if not cancel_time:
            return Command(update={
                "messages": [ToolMessage(content="Please specify the time of the booking you want to cancel.", name="cancel_event_by_time", tool_call_id=tool_call_id)]
            })

        if not email:
            return Command(update={
                "messages": [ToolMessage(content="Please provide your email to verify your booking.", name="cancel_event_by_time", tool_call_id=tool_call_id)]
            })

        target_time = parser.parse(cancel_time, fuzzy=True)

        start_dt = target_time.replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC)
        end_dt = (target_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC)

        start = start_dt.isoformat()
        end = end_dt.isoformat()

        events_result = api_resource.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])

        if not events:
            return Command(update={
                "messages": [ToolMessage(content=f"No event found around {start_dt.strftime('%I:%M %p')}.", name="cancel_event_by_time", tool_call_id=tool_call_id)]
            })

        for event in events:
            attendees = event.get('attendees', [])
            emails = [a.get('email') for a in attendees if a.get('email')]
            if email in emails:
                api_resource.events().delete(calendarId="primary", eventId=event["id"]).execute()
                return Command(update={
                    "messages": [ToolMessage(content=f"Cancelled your event: '{event['summary']}' scheduled at {start_dt.strftime('%I:%M %p on %A, %B %d')}.", name="cancel_event_by_time", tool_call_id=tool_call_id)]
                })

        return Command(update={
            "messages": [ToolMessage(content="You don’t have any event booked at that time, or the event belongs to someone else.", name="cancel_event_by_time", tool_call_id=tool_call_id)]
        })

    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(content=f"Error: {str(e)}", name="cancel_event_by_time", tool_call_id=tool_call_id)]
        })






