from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionDisplayPaymentTerms(Action):
    def name(self) -> Text:
        return "display_payment_terms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        requested_service = tracker.get_slot("requested_service")
        is_season = get_season_details(tracker.get_slot("event_date"))
        service_duration = tracker.get_slot("event_duration")
        summary = get_event_summary(tracker)
        cost = get_cost_details(requested_service, is_season, service_duration)
        payment_terms = get_payment_terms(requested_service)
        dispatcher.utter_message(summary)
        dispatcher.utter_message(cost)
        dispatcher.utter_message(payment_terms)


class ActionAskRequestBookingConfirmation(Action):
    def name(self) -> Text:
        return "action_ask_booking_confirmation"

    def run(self, dispatcher, tracker, domain):
        text = (
            f'You have requested our {tracker.get_slot("requested_service")} service '
            f'for a {tracker.get_slot("event_category")} at {tracker.get_slot("venue_location")} '
            f'on {tracker.get_slot("event_date")}, lasting for {tracker.get_slot("event_duration")} hours. '
            f"Do you wish to proceed to the service booking?"
        )

        dispatcher.utter_message(
            text=text,
            buttons=[
                {"title": "Yes", "payload": "/SetSlots(booking_confirmation=True)"},
                {"title": "No", "payload": "/SetSlots(booking_confirmation=False)"},
            ],
        )
        return []


def get_payment_terms(requested_service):
    data = {
        "photography": "50% to be paid for Booking Confirmation and balance to be paid on receiving the deliverables.",
        "videography": "50% to be paid for Booking Confirmation and balance to be paid on receiving the deliverables.",
        "360_spinner": "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
        "photo_booth": "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
        "mirror_booth": "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
    }
    return data[requested_service]


def get_season_details(date):
    season = {"start": "01/09", "end": "31/01"}
    if date >= season["start"] and date <= season["end"]:
        return True
    else:
        return False


def get_cost_details(service, is_season, service_duration):
    service_hours = int(service_duration)

    if service == "photography" or "videography" and (service_hours <= 8):
        if is_season:
            price = 200 * service_hours
        else:
            price = 150 * service_hours
    elif service == "photography" or "videography" and service_hours > 8:
        if is_season:
            price = 1200
        else:
            price = 800
    if service == "photo_booth" and service_hours >= 2:
        if is_season:
            price = 1200 + ((service_hours - 2) * 400)
        else:
            price = 1000 + ((service_hours - 2) * 400)
    if service == "360_spinner" and service_hours >= 2:
        if is_season:
            price = 1000 + ((service_hours - 2) * 300)
        else:
            price = 900 + ((service_hours - 2) * 300)
    if service == "mirror_booth" and service_hours >= 2:
        if is_season:
            price = 1500 + ((service_hours - 2) * 400)
        else:
            price = 1800 + ((service_hours - 2) * 400)
    return (
        f"Your booking for {service_duration} hours of {service} will cost {price} AED."
    )


class ActionAskIsUserInterested(Action):
    def name(self) -> Text:
        return "action_ask_is_user_interested"

    def run(self, dispatcher, tracker, domain):
        text = f"Do you wish to proceed to the service booking?"

        dispatcher.utter_message(
            text=text,
            buttons=[
                {"title": "Yes", "payload": "/SetSlots(is_user_interested=True)"},
                {"title": "No", "payload": "/SetSlots(is_user_interested=False)"},
            ],
        )
        return []


def get_event_summary(tracker):
    summary = (
        f'You have requested our {tracker.get_slot("requested_service")} service '
        f'for a {tracker.get_slot("event_category")} at {tracker.get_slot("venue_location")} '
        f'on {tracker.get_slot("event_date")}, lasting for {tracker.get_slot("event_duration")} hours. '
    )
    return summary


class ActionAskRephrase(Action):
    def name(self) -> Text:
        return "action_ask_rephrase"

    def run(self, dispatcher, tracker, domain):

        last_requested_slot = get_latest_slot_requested(tracker.events)

        if last_requested_slot:
            text = (
                f"I'm sorry, I'm not trained to understand your answer. Please adhere to one of the below formats:\n"
                + "\n".join(
                    f"{i}. {fmt}"
                    for i, fmt in enumerate(
                        accepted_formats[last_requested_slot], start=1
                    )
                )
            )
            dispatcher.utter_message(
                text=text,
            )
            dispatcher.utter_message(
                text="Let's do this again",
            )
        else:
            text = "I'm sorry, I'm unable to assist you with your request at the moment. Please try again later."

            dispatcher.utter_message(
                text=text,
            )
        return []


def get_latest_slot_requested(events_list):
    for item in reversed(events_list):  # Iterate in reverse order
        if item.get("flow_id") == "pattern_collect_information":
            return item.get("metadata", {}).get(
                "collect"
            )  # Return the collect value if found


accepted_formats = {
    "event_date": ["20th of January", "20/01/2023", "20th January 2023"]
}
