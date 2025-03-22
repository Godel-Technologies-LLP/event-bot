from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, ReminderCancelled
from rasa_sdk.events import SlotSet
from actions.utils import EventSummaryBuilder


class ServiceType(Enum):
    PHOTOGRAPHY = "photography"
    VIDEOGRAPHY = "videography"
    SPINNER_360 = "360_spinner"
    PHOTO_BOOTH = "photo_booth"
    MIRROR_BOOTH = "mirror_booth"


@dataclass
class SeasonConfig:
    start_date: str = "01/09"
    end_date: str = "31/01"


@dataclass
class ServicePricing:
    base_price: float
    hourly_rate: float
    min_hours: int
    season_multiplier: float = 1.2


class PricingCalculator:
    def __init__(self):
        self.pricing_config = {
            ServiceType.PHOTOGRAPHY: ServicePricing(
                base_price=0, hourly_rate=150, min_hours=1
            ),
            ServiceType.VIDEOGRAPHY: ServicePricing(
                base_price=0, hourly_rate=150, min_hours=1
            ),
            ServiceType.SPINNER_360: ServicePricing(
                base_price=900, hourly_rate=300, min_hours=2
            ),
            ServiceType.PHOTO_BOOTH: ServicePricing(
                base_price=1000, hourly_rate=400, min_hours=2
            ),
            ServiceType.MIRROR_BOOTH: ServicePricing(
                base_price=1800, hourly_rate=400, min_hours=2
            ),
        }

    def calculate_price(
        self, service: ServiceType, duration: int, is_season: bool
    ) -> float:
        pricing = self.pricing_config[service]
        if duration < pricing.min_hours:
            raise ValueError(
                f"Minimum duration for {service.value} is {pricing.min_hours} hours"
            )

        # Calculate base price
        if service in [ServiceType.PHOTOGRAPHY, ServiceType.VIDEOGRAPHY]:
            if duration <= 8:
                price = duration * pricing.hourly_rate
            else:
                price = 800  # Fixed price for full day
        else:
            extra_hours = max(0, duration - pricing.min_hours)
            price = pricing.base_price + (extra_hours * pricing.hourly_rate)

        # Apply season multiplier if applicable
        return price * (pricing.season_multiplier if is_season else 1.0)


class PaymentTermsManager:
    _terms = {
        ServiceType.PHOTOGRAPHY: "50% to be paid for Booking Confirmation and balance to be paid on receiving the deliverables.",
        ServiceType.VIDEOGRAPHY: "50% to be paid for Booking Confirmation and balance to be paid on receiving the deliverables.",
        ServiceType.SPINNER_360: "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
        ServiceType.PHOTO_BOOTH: "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
        ServiceType.MIRROR_BOOTH: "50% to be paid for Booking confirmation and balance to be paid on event day after finishing setup",
    }

    @classmethod
    def get_terms(cls, service: ServiceType) -> str:
        return cls._terms.get(service, "Payment terms not available for this service.")


def is_peak_season(date_str: str) -> bool:
    try:
        date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        season = SeasonConfig()
        season_start = datetime.datetime.strptime(
            f"{season.start_date}/{date.year}", "%d/%m/%Y"
        )
        season_end = datetime.datetime.strptime(
            f"{season.end_date}/{date.year}", "%d/%m/%Y"
        )
        return season_start <= date <= season_end
    except ValueError:
        return False


class ActionDisplayPaymentTerms(Action):
    def __init__(self):
        self.pricing_calculator = PricingCalculator()

    def name(self) -> Text:
        return "display_payment_terms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        try:
            event_details = EventSummaryBuilder.event_details(tracker)

            # Get slot values
            service = ServiceType(event_details.requested_service)
            date_str = event_details.event_date
            duration = int(event_details.event_duration)

            is_season = is_peak_season(date_str)
            price = self.pricing_calculator.calculate_price(
                service, duration, is_season
            )
            cost_message = f"Your booking for {duration} hours of {service.value} will cost {price:.2f} AED."
            payment_terms = PaymentTermsManager.get_terms(service)

            # Send messages
            dispatcher.utter_message(text=cost_message)
            dispatcher.utter_message(text=payment_terms)

        except (ValueError, KeyError) as e:
            dispatcher.utter_message(
                text=f"Sorry, there was an error processing your request: {str(e)}"
            )

        return []
