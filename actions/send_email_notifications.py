from typing import Any, Text, Dict, List
import boto3
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSendBookingConfirmation(Action):
    def name(self) -> Text:
        return "action_send_booking_confirmation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Extract slots from Rasa tracker
        event_date = tracker.get_slot("event_date")
        event_duration = tracker.get_slot("event_duration")
        venue_location = tracker.get_slot("venue_location")
        event_category = tracker.get_slot("event_category")
        requested_service = tracker.get_slot("requested_service")

        # Ensure all slots are filled
        if not all(
            [
                event_date,
                event_duration,
                venue_location,
                event_category,
                requested_service,
            ]
        ):
            dispatcher.utter_message(
                text="Some event details are missing. Please provide complete information."
            )
            return []

        # AWS SNS client
        sns_client = boto3.client("sns", region_name="us-east-1")

        # Email subject and message
        email_subject = f"Booking Confirmation - Your Event on {event_date}"
        email_message = f"""
        Thank you for booking with us! Here are the details of your upcoming event:

        📅 Event Date: {event_date}
        ⏳ Duration: {event_duration} hours
        📍 Venue Location: {venue_location}
        🎭 Event Category: {event_category}
        📷 Requested Service: {requested_service}

        We’re excited to be part of your special event!
        Looking forward to serving you!

        Best Regards,  
        iClick Services  
        📩 bookings@iclick.com  
        🌐 www.iclick.com
        """

        # SNS Topic ARN (Replace with your actual SNS Topic ARN)
        sns_topic_arn = ""

        try:
            # Publish message to SNS
            response = sns_client.publish(
                TopicArn=sns_topic_arn, Message=email_message, Subject=email_subject
            )
            dispatcher.utter_message(
                text="Your confirmation email has been sent! Please check your inbox (and spam folder, just in case)."
            )
            print("SNS Email Notification Sent! Message ID:", response["MessageId"])

        except Exception as e:
            dispatcher.utter_message(
                text="Failed to send the booking confirmation email. "
            )
            print("Error:", str(e))

        return []
