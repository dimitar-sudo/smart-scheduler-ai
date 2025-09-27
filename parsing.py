import spacy
import json
import datetime
from dateutil import parser
import re

nlp = spacy.load("en_core_web_md")

text = input("Enter reservation details: ")

# Preprocess text to handle common reservation patterns
doc = nlp(text)

reservation = {
    "name": None,
    "date": None,
    "time": None
}

# List of words that should never be considered as names
excluded_names = ["the", "a", "an", "this", "that", "these", "those", 
                 "today", "tomorrow", "yesterday", "monday", "tuesday", 
                 "wednesday", "thursday", "friday", "saturday", "sunday",
                 "morning", "afternoon", "evening", "night", "pm", "am",
                 "january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"]

# Extract entities with better filtering
for ent in doc.ents:
    if ent.label_ == "PERSON":
        # Exclude common words and date/time words from being saved as names
        if (ent.text.lower() not in excluded_names and 
            len(ent.text) > 1 and  # Single characters are unlikely to be names
            not ent.text.isdigit() and  # Numbers aren't names
            not any(date_word in ent.text.lower() for date_word in ["today", "tomorrow", "yesterday"]) and
            not any(day in ent.text.lower() for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])):
            reservation["name"] = ent.text
    elif ent.label_ == "DATE":
        try:
            # Handle relative dates like "today", "tomorrow", etc.
            date_text = ent.text.lower()
            today = datetime.datetime.now()
            
            if date_text == "today":
                reservation["date"] = today.strftime("%d.%m.%Y")
            elif date_text == "tomorrow":
                tomorrow = today + datetime.timedelta(days=1)
                reservation["date"] = tomorrow.strftime("%d.%m.%Y")
            elif date_text == "yesterday":
                yesterday = today - datetime.timedelta(days=1)
                reservation["date"] = yesterday.strftime("%d.%m.%Y")
            else:
                # Clean the date text and parse
                date_text = date_text.replace("next ", "").replace("this ", "")
                parsed_date = parser.parse(date_text, fuzzy=True)
                reservation["date"] = parsed_date.strftime("%d.%m.%Y")
        except:
            # Handle relative dates like "next monday"
            try:
                today = datetime.datetime.now()
                weekday_map = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                
                for day_name, day_num in weekday_map.items():
                    if day_name in ent.text.lower():
                        # Calculate days until next specific weekday
                        days_ahead = (day_num - today.weekday() + 7) % 7
                        if days_ahead == 0:  # If today is that day, get next week
                            days_ahead = 7
                        next_day = today + datetime.timedelta(days=days_ahead)
                        reservation["date"] = next_day.strftime("%d.%m.%Y")
                        break
                else:
                    reservation["date"] = ent.text
            except:
                reservation["date"] = ent.text
    elif ent.label_ == "TIME":
        # Clean the time text
        time_text = ent.text
        try:
            parsed_time = parser.parse(time_text)
            reservation["time"] = parsed_time.strftime("%H:%M")
        except:
            reservation["time"] = time_text

# Fallback: if entities weren't properly detected, use pattern matching
if not reservation["name"]:
    # Look for name after "under", "for", or "name"
    name_patterns = [
        r"under\s+the\s+name\s+(\w+)",
        r"under\s+(\w+)",
        r"for\s+(\w+)$",
        r"name\s+(\w+)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name_candidate = match.group(1)
            # Exclude common words from being saved as names
            if (name_candidate.lower() not in excluded_names and 
                len(name_candidate) > 1 and
                not name_candidate.isdigit()):
                reservation["name"] = name_candidate
                break

# Improved time parsing that handles "9 in the afternoon"
if not reservation["time"] or any(word in str(reservation["time"]).lower() for word in ["afternoon", "morning", "evening", "night"]):
    # Look for various time patterns including "9 in the afternoon"
    time_patterns = [
        r'(\d{1,2})\s*(?:o\'?clock)?\s*(?:in the\s+)?(afternoon|evening|morning|night)',
        r'(\d{1,2})\s*(?:o\'?clock)?\s*(am|pm)',
        r'(\d{1,2})(?::\d{2})?\s*(am|pm)',
        r'(\d{1,2})(?::\d{2})?\s*(?:in the\s+)?(afternoon|evening|morning|night)'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            # Safely get the period group
            period = None
            if match.lastindex >= 2:
                period = match.group(2).lower() if match.group(2) else None
            
            # Convert to 24-hour format
            if period in ['pm', 'afternoon', 'evening', 'night']:
                if hour < 12:
                    hour += 12
            elif period in ['am', 'morning'] and hour == 12:
                hour = 0
                
            reservation["time"] = f"{hour:02d}:00"
            break

if not reservation["date"]:
    # Look for date patterns or relative dates including "today", "tomorrow"
    today = datetime.datetime.now()
    
    # Check for relative dates first
    if re.search(r'\btoday\b', text, re.IGNORECASE):
        reservation["date"] = today.strftime("%d.%m.%Y")
    elif re.search(r'\btomorrow\b', text, re.IGNORECASE):
        tomorrow = today + datetime.timedelta(days=1)
        reservation["date"] = tomorrow.strftime("%d.%m.%Y")
    elif re.search(r'\byesterday\b', text, re.IGNORECASE):
        yesterday = today - datetime.timedelta(days=1)
        reservation["date"] = yesterday.strftime("%d.%m.%Y")
    else:
        # Check for weekday patterns
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Check for "next monday" type patterns
        next_day_match = re.search(r'next\s+(\w+)', text, re.IGNORECASE)
        if next_day_match:
            day_name = next_day_match.group(1).lower()
            if day_name in weekday_map:
                day_num = weekday_map[day_name]
                days_ahead = (day_num - today.weekday() + 7) % 7
                if days_ahead == 0:  # If today is that day, get next week
                    days_ahead = 7
                next_day = today + datetime.timedelta(days=days_ahead)
                reservation["date"] = next_day.strftime("%d.%m.%Y")
        else:
            # Check for simple weekday names
            for day_name, day_num in weekday_map.items():
                if re.search(r'\b' + day_name + r'\b', text, re.IGNORECASE):
                    days_ahead = (day_num - today.weekday() + 7) % 7
                    if days_ahead == 0:  # If today is that day, use today
                        reservation["date"] = today.strftime("%d.%m.%Y")
                    else:
                        next_day = today + datetime.timedelta(days=days_ahead)
                        reservation["date"] = next_day.strftime("%d.%m.%Y")
                    break

# NEW FEATURE: Prompt user for missing information with better validation
if not reservation["name"] or reservation["name"].lower() in excluded_names:
    name_input = input("Please enter the name for the appointment: ")
    # Validate the name input
    if (name_input.strip().lower() not in excluded_names and 
        len(name_input.strip()) > 1 and
        not name_input.strip().isdigit()):
        reservation["name"] = name_input.strip()
    else:
        print("Invalid name. Please enter a valid name.")
        # Retry until valid name is entered
        while True:
            name_input = input("Please enter a valid name for the appointment: ")
            if (name_input.strip().lower() not in excluded_names and 
                len(name_input.strip()) > 1 and
                not name_input.strip().isdigit()):
                reservation["name"] = name_input.strip()
                break
            else:
                print("Invalid name. Please try again.")

if not reservation["date"]:
    date_input = input("Please enter the date for the appointment: ")
    # Try to normalize the entered date
    try:
        # Handle relative dates in user input too
        date_input_lower = date_input.lower()
        today = datetime.datetime.now()
        
        if date_input_lower == "today":
            reservation["date"] = today.strftime("%d.%m.%Y")
        elif date_input_lower == "tomorrow":
            tomorrow = today + datetime.timedelta(days=1)
            reservation["date"] = tomorrow.strftime("%d.%m.%Y")
        elif date_input_lower == "yesterday":
            yesterday = today - datetime.timedelta(days=1)
            reservation["date"] = yesterday.strftime("%d.%m.%Y")
        else:
            parsed_date = parser.parse(date_input, fuzzy=True)
            reservation["date"] = parsed_date.strftime("%d.%m.%Y")
    except:
        reservation["date"] = date_input.strip()

if not reservation["time"]:
    time_input = input("Please enter the time for the appointment: ")
    # Try to normalize the entered time
    try:
        parsed_time = parser.parse(time_input)
        reservation["time"] = parsed_time.strftime("%H:%M")
    except:
        # Try pattern matching for time expressions
        time_patterns = [
            r'(\d{1,2})\s*(?:o\'?clock)?\s*(?:in the\s+)?(afternoon|evening|morning|night)',
            r'(\d{1,2})\s*(?:o\'?clock)?\s*(am|pm)',
        ]
        
        time_found = False
        for pattern in time_patterns:
            match = re.search(pattern, time_input, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                period = None
                if match.lastindex >= 2:
                    period = match.group(2).lower() if match.group(2) else None
                
                if period in ['pm', 'afternoon', 'evening', 'night']:
                    if hour < 12:
                        hour += 12
                elif period in ['am', 'morning'] and hour == 12:
                    hour = 0
                    
                reservation["time"] = f"{hour:02d}:00"
                time_found = True
                break
        
        if not time_found:
            reservation["time"] = time_input.strip()

print(f"{reservation['name']} your appointment has been made for {reservation['date']} at {reservation['time']}.")