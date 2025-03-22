from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, ReminderCancelled
from rasa_sdk.events import SlotSet
from actions.db import get_bookings, save_booking, Booking, EventDetails
from actions.utils import get_indices, EventSummaryBuilder


class ListBookings(Action):

    def name(self) -> str:
        return "list_bookings"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]
    ):
        email = tracker.get_slot("customer_email")

        bookings = get_bookings()
        existing_emails = [b.email for b in bookings]
        indices = get_indices(email, existing_emails)
        if indices is None:
            dispatcher.utter_message(text="No booking found for this email.")
            return []
        else:
            for i in indices:
                dispatcher.utter_message(
                    text=f"Your bookings for this email-ID are:\n{EventSummaryBuilder.build_summary(bookings[i].event_details)}"
                )
            return []
