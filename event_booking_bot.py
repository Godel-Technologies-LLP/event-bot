from rag import query_llm, generate_confirmation

def extract_exact_match(llm_response, valid_options):
    """Extracts the exact service/event name from the LLM response."""
    llm_response = llm_response.lower()
    
    for option in valid_options:
        if option.lower() in llm_response:
            return option  # Return exact match
    
    return None  # No valid match found

def confirm_detail(detail_type, expected_value, user_memory):
    """Asks the user to confirm a detail they previously provided and stores it."""
    while True:
        confirmation = input(f"\n🤖 Can you confirm {detail_type}? ").strip().lower()
        
        if "what i have given" in confirmation:
            print(f"🔍 You previously entered: {expected_value}")
            continue  # Ask again

        if expected_value.lower() in confirmation:
            print("✅ That's correct!")
            user_memory[detail_type] = expected_value  # Store in memory
            return True

        print("❌ That doesn't match. Please try again.")

def chatbot():
    """Interactive chatbot using an LLM for processing user input."""
    print("👋 Welcome to iClick! Make your events more fun and memorable with our services.")
    
    # Store user inputs for later retrieval
    user_memory = {}

    # Predefined options
    services = ["Photography", "Videography", "360 Spinner", "Photo Booth", "Mirror Booth"]
    events = ["Exhibition", "Conference", "Seminar", "Annual Party", "Birthday Party", "Anniversary"]

    # Step 1: Ask for service (Processed by LLM)
    while True:
        print("\n➡ Type of service required?")
        print("\n".join(services))  # Display services
        user_input = input("\nYou: ").strip()
        
        llm_response = query_llm(user_input, services)  # Extract using LLM
        requested_service = extract_exact_match(llm_response, services)  # Strict extraction
        
        print(f"🛠️ LLM Response: {llm_response}")
        print(f"🛠️ Extracted Service: {requested_service}")

        if requested_service:
            user_memory["service"] = requested_service  # Store in memory
            break
        print("\n❌ Invalid choice. Please select from the available services.")

    # Step 2: Confirm Service Selection
    confirm_detail("which service you selected", user_memory["service"], user_memory)

    # Step 3: Ask for event type (Processed by LLM)
    while True:
        print("\n➡ Type of event?")
        print("\n".join(events))  # Display event options
        user_input = input("\nYou: ").strip()

        llm_response = query_llm(user_input, events)  # Corrected LLM query
        extracted_event = extract_exact_match(llm_response, events)  # Strict extraction

        print(f"🛠️ LLM Response: {llm_response}")
        print(f"🛠️ Extracted Event: {extracted_event}")

        if extracted_event:
            user_memory["event"] = extracted_event  # Store valid event
            break
        print("\n❌ Invalid choice. Please select from the available event types.")

    # Step 4: Confirm Event Type
    confirm_detail("the type of event you selected", user_memory["event"], user_memory)

    # Step 5: Ask for event details
    while True:
        event_date = input("\n📅 When is the event date? (DD/MM/YYYY): ").strip()
        
        if "what i have given" in event_date.lower():
            if "event_date" in user_memory:
                print(f"🔍 You previously entered: {user_memory['event_date']}")
                continue  # Ask again
            else:
                print("❌ No event date was provided yet. Please enter one.")
                continue
        
        user_memory["event_date"] = event_date  # Store event date
        break

    event_duration = input("\n⏳ For how long do you need our service? (in hours): ")
    event_location = input("\n📍 What is the event location (City Name)?: ")

    # Step 6: Confirm Event Date
    confirm_detail("when the event is scheduled", user_memory["event_date"], user_memory)

    # Generate confirmation message
    response = generate_confirmation(user_memory["service"], user_memory["event"], user_memory["event_date"], event_duration, event_location)
    print("\nBot:", response)

    # Step 7: Ask for confirmation
    confirmation = input("\nYou: ").strip().lower()
    
    if confirmation == "yes":
        user_email = input("\n📧 Please share your email: ")
        print("\n✅ Your booking has been confirmed! A confirmation email will be sent to", user_email)
    else:
        print("\n❌ Booking not confirmed. Let us know if you need assistance!")

# Run chatbot
if __name__ == "__main__":
    chatbot()
