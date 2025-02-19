from rag import query_llm, generate_confirmation

def extract_exact_match(llm_response, valid_options):
    """
    Extracts the exact service/event name from the LLM response.
    Ensures the response is one of the predefined options.
    """
    for option in valid_options:
        if option.lower() in llm_response.lower():
            return option
    return None  # If no valid match is found

def chatbot():
    """Interactive chatbot using an LLM for processing user input."""
    print("👋 Welcome to iClick! Make your events more fun and memorable with our services.")
    
    # Predefined options
    services = ["Photography", "Videography", "360 Spinner", "Photo Booth", "Mirror Booth"]
    events = ["Exhibition", "Conference", "Seminar", "Annual Party", "Birthday Party", "Anniversary"]

    # Step 1: Ask for service (Processed by LLM)
    while True:
        print("\n➡ Type of service required?")
        print("\n".join(services))  # Display services
        user_input = input("\nYou: ").strip()
        
        llm_response = query_llm(user_input, services)  # Extract using LLM
        requested_service = extract_exact_match(llm_response, services)  # Fix extraction
        
        # Debugging
        print(f"🛠️ LLM Response: {llm_response}")
        print(f"🛠️ Extracted Service: {requested_service}")

        if requested_service:
            break
        print("\n❌ Invalid choice. Please select from the available services.")

    # Step 2: Ask for event type (Processed by LLM)
    while True:
        print("\n➡ Type of event?")
        print("\n".join(events))  # Display events
        user_input = input("\nYou: ").strip()

        llm_response = query_llm(user_input, events)
        event_category = extract_exact_match(llm_response, events)  # Fix extraction

        # Debugging
        print(f"🛠️ LLM Response: {llm_response}")
        print(f"🛠️ Extracted Event: {event_category}")

        if event_category:
            break
        print("\n❌ Invalid choice. Please select from the available event types.")

    # Step 3: Ask for event details
    event_date = input("\n📅 When is the event date? (DD/MM/YYYY): ")
    event_duration = input("\n⏳ For how long do you need our service? (in hours): ")
    event_location = input("\n📍 What is the event location (City Name)?: ")

    # Generate confirmation message
    response = generate_confirmation(requested_service, event_category, event_date, event_duration, event_location)
    print("\nBot:", response)

    # Step 4: Ask for confirmation
    confirmation = input("\nYou: ").strip().lower()
    
    if confirmation == "yes":
        user_email = input("\n📧 Please share your email: ")
        print("\n✅ Your booking has been confirmed! A confirmation email will be sent to", user_email)
    else:
        print("\n❌ Booking not confirmed. Let us know if you need assistance!")

# Run chatbot
if __name__ == "__main__":
    chatbot()
