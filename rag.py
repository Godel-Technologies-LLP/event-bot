import openai
import os
from dotenv import load_dotenv
from vector_db import retrieve_service

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_llm(prompt, valid_options):
    """Query GPT-4 for dynamic responses and validate against given options."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7
    )
    
    extracted_value = response["choices"][0]["message"]["content"].strip().lower()

    # Debugging: Print LLM Response
    print(f"\n🛠️ LLM Response: {extracted_value}")

    # Validate extracted value against provided options
    for option in valid_options:
        if option.lower() in extracted_value:
            return option  # Return valid option
    
    return None  # Return None if no valid option is found



def generate_questions():
    """You are an AI event booking assistant. Your task is to strictly follow the conversation structure below. 
    Do NOT add extra explanations or descriptions. Only ask the required question based on the stage in the conversation.

    Example conversation:

    👋 Welcome to iClick! Make your events more fun and memorable with our services.

    ➡ Type of service required?
    - Photography
    - Videography
    - 360 Spinner
    - Photo Booth
    - Mirror Booth

    User: [User selects service]

    ➡ Type of event?
    - Exhibition
    - Conference
    - Seminar
    - Annual Party
    - Birthday Party
    - Anniversary

    User: [User selects event type]

    ➡ When is the event date? (DD/MM/YYYY)

    User: [User enters date]

    ➡ For how long do you need our service? (in hours)

    User: [User enters duration]

    ➡ What is the event location (City Name)?

    User: [User enters location]

    ✅ Summary:
    - Service: [Extracted service]
    - Event Type: [Extracted event]
    - Date: [Extracted date]
    - Duration: [Extracted hours]
    - Location: [Extracted location]

    💰 Booking Details:
    - Estimated cost: [Auto-generate cost based on service & duration]
    - Payment: 50% upfront, 50% on deliverables
    - Proceed with booking?

    User: Yes/No

    ➡ If Yes → Ask for email confirmation  
    ➡ If No → Stop conversation politely

    User: [User provides email]

    ✅ Your booking has been confirmed! A confirmation email will be sent to [User email].

    IMPORTANT RULES:
    - Do NOT add explanations.
    - Stick to the script.
    - If user input is unclear, ask them to re-enter.
    - Stop after email confirmation.
    
    Begin the conversation:

    👋 Welcome to iClick! Make your events more fun and memorable with our services.
    ➡ Type of service required?
    """
    
    return query_llm(prompt).split("\n")
def generate_confirmation(service, event, date, duration, location):
    """
    Generate a confirmation message for the booking.
    """
    prompt = f"""
    You have requested our {service} service for a {event} at {location} on {date}, lasting for {duration} hours.
    Your booking for {duration} hours of {service} will cost 350 AED.
    50% to be paid for Booking Confirmation and balance to be paid on receiving the deliverables.
    Do you wish to proceed to the service booking?
    Yes
    No
    """
    
    # Pass an empty list as valid_options to prevent error
    return query_llm(prompt, [])  # ✅ Fix: Added second argument
