from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, ReminderCancelled, SlotSet
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI

client = OpenAI()


class ActionSetReminder(Action):
    """Schedules a reminder"""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # set a timer for 15 seconds:
        date = datetime.datetime.now() + datetime.timedelta(minutes=0.1)

        # Required: pass params to Reminder Object. For more info visit:
        # https://rasa.com/docs/rasa-pro/nlu-based-assistants/reaching-out-to-user#reminders
        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            name="reminder",
            kill_on_user_message=True,
        )

        return [reminder]


class ForgetReminders(Action):
    """Cancels all reminders."""

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # Cancel all reminders
        return [ReminderCancelled()]


# class ValidateRequestedService(Action):
#     """Validates the service"""

#     def name(self) -> Text:
#         return "validate_requested_service"

#     async def run(
#         self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         # Cancel all reminders
#         dispatcher.utter_message(text="I am in validate requested service")
#         return []


# class ValidateEventType(Action):
#     """Validates the eventy"""

#     def name(self) -> Text:
#         return "validate_event_category"

#     async def run(
#         self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         # Cancel all reminders
#         dispatcher.utter_message(text="I am in validate event_category")
#         return []


def get_indices(email, existing_emails):
    return [i for i, x in enumerate(existing_emails) if x == email]


class EventDetails(BaseModel):
    """Model representing event details."""

    event_date: str
    event_duration: float
    venue_location: str
    requested_service: str
    event_category: str


class EventSummaryBuilder:
    @staticmethod
    def build_summary(event_details: EventDetails) -> str:
        return (
            f"You have requested our {event_details.requested_service} service "
            f"for {event_details.event_category} at {event_details.venue_location} "
            f"on {event_details.event_date}, lasting for {event_details.event_duration} hours."
        )

    @staticmethod
    def event_details(tracker: Tracker) -> EventDetails:
        raw_details = {
            "event_date": tracker.get_slot("event_date"),
            "event_duration": tracker.get_slot("event_duration"),
            "venue_location": tracker.get_slot("venue_location"),
            "requested_service": tracker.get_slot("requested_service").replace(
                "_", " "
            ),
            "event_category": tracker.get_slot("event_category").replace("_", " "),
        }
        return EventDetails(**raw_details)


class CorrectEventDateTime(Action):
    """Correct current date-time"""

    def name(self) -> Text:
        return "action_correct_event_date"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Get the current datetime
        format = "%d-%m-%Y"

        # Convert datetime to string
        current_date_time_str = datetime.now().strftime(format)
        last_message = tracker.latest_message.get("text")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "developer",
                    "content": "use the current date and the date user is mentioning to return the output in DD/MM/YYYY format. Just return DD/MM/YYYY. No more text",
                },
                {
                    "role": "user",
                    "content": f"Current datetime:{current_date_time_str} user message: {last_message}",
                },
            ],
        )
        event_date = completion.choices[0].message.content

        return [SlotSet("event_date", event_date)]
