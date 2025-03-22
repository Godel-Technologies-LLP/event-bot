from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, ReminderCancelled
from rasa_sdk.events import SlotSet
from actions.db import get_bookings, save_booking, Booking
from actions.utils import EventSummaryBuilder, get_indices

# class ActionAskRequestBookingConfirmation(Action):
#     def name(self) -> Text:
#         return "action_ask_booking_confirmation"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         summary = EventSummaryBuilder.build_summary(tracker)
#         text = f"{summary}\nDo you wish to proceed to the service booking?"

#         dispatcher.utter_message(
#             text=text,
#             buttons=[
#                 {"title": "Yes", "payload": "/SetSlots(booking_confirmation=True)"},
#                 {"title": "No", "payload": "/SetSlots(booking_confirmation=False)"},
#             ],
#         )
#         return []


class ActionAskIsUserInterested(Action):
    def name(self) -> Text:
        return "action_ask_is_user_interested"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Do you wish to proceed to check availability??",
        )
        return []


class ActionAskRephrase(Action):
    ACCEPTED_FORMATS = {
        "event_date": ["DD/MM/YYYY", "20th of January 2024", "20th January 2024"],
        "requested_service": [
            "Photography",
            "Videography",
            "360 Spinner",
            "Photo Booth",
            "Mirror Booth",
        ],
        "event_category": [
            "Exhibition",
            "Conference",
            "Seminar",
            "Annual Party",
            "Birthday Party",
            "Anniversary",
        ],
    }

    def name(self) -> Text:
        return "action_ask_rephrase"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        last_requested_slot = self._get_latest_slot_requested(tracker.events)
        formats = self.ACCEPTED_FORMATS.get(last_requested_slot, [])
        format_text = "\n".join(f"{i}. {fmt}" for i, fmt in enumerate(formats, start=1))

        if last_requested_slot in ["requested_service", "event_category"]:

            dispatcher.utter_message(
                text=f"I'm sorry, I didn't understand your answer. Please use one of these options:\n{format_text}"
            )
            dispatcher.utter_message(text="Let's try again")
        elif last_requested_slot == "event_date":
            dispatcher.utter_message(
                text=f"I'm sorry, I didn't understand your answer. Please provide the date in one of these formats:\n{format_text}"
            )
            dispatcher.utter_message(text="Let's try again")
        elif last_requested_slot == "venue_location":
            dispatcher.utter_message(
                text=f"Our search returned that there is no such location. We could be wrong, too. Can you reconfirm"
            )

        else:
            dispatcher.utter_message(
                text="I'm sorry, I'm unable to process your request at the moment. Please try again later."
            )
        return []

    @staticmethod
    def _get_latest_slot_requested(events_list: List[Dict[str, Any]]) -> Optional[str]:
        for event in reversed(events_list):
            if event.get("flow_id") == "pattern_collect_information":
                return event.get("metadata", {}).get("collect")
        return None


class SaveBooking(Action):

    def name(self) -> str:
        return "save_booking"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]
    ):
        bookings = get_bookings()
        email = tracker.get_slot("customer_email")
        event_details = EventSummaryBuilder.event_details(tracker)

        existing_emails = [b.email for b in bookings]
        indices = get_indices(email, existing_emails)
        if indices is not None:
            # Get the index of the email in existing emails
            for index in indices:
                if bookings[index].event_details == event_details:
                    dispatcher.utter_message(
                        text="You have already made a booking for this event."
                    )
                    return []
                    # message for existing booking.
                dispatcher.utter_message(
                    text=f"There is an active previous booking made with this email-ID. The details are:\n{EventSummaryBuilder.build_summary(bookings[index].event_details)}"
                )

            new_booking = Booking(
                email=email,
                event_details=event_details,
            )
            save_booking(new_booking)
            dispatcher.utter_message(
                text=f" Your current booking details are:\n{EventSummaryBuilder.build_summary(event_details)}"
            )

            return []
        else:
            new_booking = Booking(
                email=email,
                event_details=event_details,
            )
            save_booking(new_booking)
            dispatcher.utter_message(
                text=f" Your current booking details are:\n{EventSummaryBuilder.build_summary(event_details)}"
            )
            return []
