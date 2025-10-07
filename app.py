import spacy
import json
import datetime
from dateutil import parser
import re

nlp = spacy.load("en_core_web_md")

text = input("Enter reservation details: ")

doc = nlp(text)

reservation = {
    "title": None,   
    "start": None, 
    "end": None,   
    "allDay": False,
    "description": 'Reservation made via chatbot'
}

excluded_names = ["the", "a", "an", "this", "that", "these", "those", 
                 "today", "tomorrow", "yesterday", "monday", "tuesday", 
                 "wednesday", "thursday", "friday", "saturday", "sunday",
                 "morning", "afternoon", "evening", "night", "pm", "am",
                 "january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"]

def is_time_expression(text):
    time_patterns = [
        r'^\d{1,2}\s*(?:am|pm)$',
        r'^\d{1,2}:\d{2}\s*(?:am|pm)?$',
        r'^\d{1,2}\s*(?:o\'?clock)?\s*(?:in the\s+)?(afternoon|evening|morning|night)$',
    ]
    for pattern in time_patterns:
        if re.search(pattern, text.lower()):
            return True
    return False

for ent in doc.ents:
    if ent.label_ == "PERSON":
        if (ent.text.lower() not in excluded_names and 
            len(ent.text) > 1 and
            not ent.text.isdigit() and
            not any(date_word in ent.text.lower() for date_word in ["today", "tomorrow", "yesterday"]) and
            not any(day in ent.text.lower() for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) and
            not is_time_expression(ent.text)):
            reservation["title"] = ent.text + " Appointment"
    elif ent.label_ == "DATE":
        try:
            date_text = ent.text.lower()
            today = datetime.datetime.now()
            
            if date_text == "today":
                reservation["start"] = today.strftime("%d.%m.%Y")
            elif date_text == "tomorrow":
                tomorrow = today + datetime.timedelta(days=1)
                reservation["start"] = tomorrow.strftime("%d.%m.%Y")
            elif date_text == "yesterday":
                yesterday = today - datetime.timedelta(days=1)
                reservation["start"] = yesterday.strftime("%d.%m.%Y")
            else:
                date_text = date_text.replace("next ", "").replace("this ", "")
                parsed_date = parser.parse(date_text, fuzzy=True)
                reservation["start"] = parsed_date.strftime("%d.%m.%Y")
        except:
            try:
                today = datetime.datetime.now()
                weekday_map = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                
                for day_name, day_num in weekday_map.items():
                    if day_name in ent.text.lower():
                        days_ahead = (day_num - today.weekday() + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                        next_day = today + datetime.timedelta(days=days_ahead)
                        reservation["start"] = next_day.strftime("%d.%m.%Y")
                        break
                else:
                    reservation["start"] = ent.text
            except:
                reservation["start"] = ent.text
    elif ent.label_ == "TIME":
        time_text = ent.text
        try:
            parsed_time = parser.parse(time_text)
            reservation["end"] = parsed_time.strftime("%H:%M")
        except:
            reservation["end"] = time_text

if not reservation["title"]:
    name_patterns = [
        r"under\s+the\s+name\s+of\s+([a-zA-Z\s]+)",
        r"under\s+([a-zA-Z\s]+)",
        r"for\s+([a-zA-Z\s]+)(?:\s+on|\s+at|$)",
        r"name\s+is\s+([a-zA-Z\s]+)",
        r"reservation\s+for\s+([a-zA-Z\s]+)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name_candidate = match.group(1).strip()
            if (name_candidate.lower() not in excluded_names and 
                len(name_candidate) > 1 and
                not name_candidate.isdigit() and
                not is_time_expression(name_candidate)):
                reservation["title"] = name_candidate + " Appointment"
                break

def is_within_working_hours(time_str):
    try:
        if isinstance(time_str, str):
            time_obj = parser.parse(time_str).time()
        else:
            time_obj = time_str
            
        start_time = datetime.time(9, 0)
        end_time = datetime.time(17, 0)
        
        return start_time <= time_obj <= end_time
    except:
        return False

if not reservation["end"] or any(word in str(reservation["end"]).lower() for word in ["afternoon", "morning", "evening", "night"]):
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
            period = None
            if match.lastindex >= 2:
                period = match.group(2).lower() if match.group(2) else None
            
            if period in ['pm', 'afternoon', 'evening', 'night']:
                if hour < 12:
                    hour += 12
            elif period in ['am', 'morning'] and hour == 12:
                hour = 0
                
            reservation["end"] = f"{hour:02d}:00"
            break

if not reservation["start"]:
    today = datetime.datetime.now()
    
    if re.search(r'\btoday\b', text, re.IGNORECASE):
        reservation["start"] = today.strftime("%d.%m.%Y")
    elif re.search(r'\btomorrow\b', text, re.IGNORECASE):
        tomorrow = today + datetime.timedelta(days=1)
        reservation["start"] = tomorrow.strftime("%d.%m.%Y")
    elif re.search(r'\byesterday\b', text, re.IGNORECASE):
        yesterday = today - datetime.timedelta(days=1)
        reservation["start"] = yesterday.strftime("%d.%m.%Y")
    else:
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        next_day_match = re.search(r'next\s+(\w+)', text, re.IGNORECASE)
        if next_day_match:
            day_name = next_day_match.group(1).lower()
            if day_name in weekday_map:
                day_num = weekday_map[day_name]
                days_ahead = (day_num - today.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                next_day = today + datetime.timedelta(days=days_ahead)
                reservation["start"] = next_day.strftime("%d.%m.%Y")
        else:
            for day_name, day_num in weekday_map.items():
                if re.search(r'\b' + day_name + r'\b', text, re.IGNORECASE):
                    days_ahead = (day_num - today.weekday() + 7) % 7
                    if days_ahead == 0:
                        reservation["start"] = today.strftime("%d.%m.%Y")
                    else:
                        next_day = today + datetime.timedelta(days=days_ahead)
                        reservation["start"] = next_day.strftime("%d.%m.%Y")
                    break

if not reservation["title"] or reservation["title"].lower() in excluded_names or is_time_expression(reservation["title"] or ""):
    name_input = input("Please enter the name for the appointment: ")
    if (name_input.strip().lower() not in excluded_names and 
        len(name_input.strip()) > 1 and
        not name_input.strip().isdigit() and
        not is_time_expression(name_input.strip())):
        reservation["title"] = name_input.strip() + " Appointment"
    else:
        print("Invalid name. Please enter a valid name.")
        while True:
            name_input = input("Please enter a valid name for the appointment: ")
            if (name_input.strip().lower() not in excluded_names and 
                len(name_input.strip()) > 1 and
                not name_input.strip().isdigit() and
                not is_time_expression(name_input.strip())):
                reservation["title"] = name_input.strip() + " Appointment"
                break
            else:
                print("Invalid name. Please try again.")

if not reservation["start"]:
    date_input = input("Please enter the date for the appointment: ")
    try:
        date_input_lower = date_input.lower()
        today = datetime.datetime.now()
        
        if date_input_lower == "today":
            reservation["start"] = today.strftime("%d.%m.%Y")
        elif date_input_lower == "tomorrow":
            tomorrow = today + datetime.timedelta(days=1)
            reservation["start"] = tomorrow.strftime("%d.%m.%Y")
        elif date_input_lower == "yesterday":
            yesterday = today - datetime.timedelta(days=1)
            reservation["start"] = yesterday.strftime("%d.%m.%Y")
        else:
            parsed_date = parser.parse(date_input, fuzzy=True)
            reservation["start"] = parsed_date.strftime("%d.%m.%Y")
    except:
        reservation["start"] = date_input.strip()

if not reservation["end"]:
    while True:
        time_input = input("Please enter the time for the appointment: ")
        try:
            parsed_time = parser.parse(time_input)
            time_obj = parsed_time.time()
            reservation["end"] = parsed_time.strftime("%H:%M")
            
            if not is_within_working_hours(time_obj):
                print("The time you entered is outside working hours (09:00 - 17:00).")
                continue_option = input("Would you like to enter a different time? (yes/no): ")
                if continue_option.lower() in ['yes', 'y']:
                    reservation["end"] = None
                    continue
                else:
                    break
            else:
                break
                
        except:
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
                        
                    time_obj = datetime.time(hour, 0)
                    reservation["end"] = f"{hour:02d}:00"
                    
                    if not is_within_working_hours(time_obj):
                        print("The time you entered is outside working hours (09:00 - 17:00).")
                        continue_option = input("Would you like to enter a different time? (yes/no): ")
                        if continue_option.lower() in ['yes', 'y']:
                            reservation["end"] = None
                            continue
                    
                    time_found = True
                    break
            
            if not time_found:
                reservation["end"] = time_input.strip()
            break

elif reservation["end"]:
    try:
        time_obj = parser.parse(reservation["end"]).time()
        if not is_within_working_hours(time_obj):
            print(f"The time {reservation['end']} is outside working hours (09:00 - 17:00).")
            response = input("Would you like to change the time? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                while True:
                    new_time_input = input("Please enter a new time within working hours (09:00-17:00): ")
                    try:
                        parsed_time = parser.parse(new_time_input)
                        new_time_obj = parsed_time.time()
                        if is_within_working_hours(new_time_obj):
                            reservation["end"] = parsed_time.strftime("%H:%M")
                            break
                        else:
                            print("This time is still outside working hours. Please try again.")
                    except:
                        print("Invalid time format. Please try again.")
    except:
        pass

if reservation["start"] and reservation["end"]:
    try:
        start_date = parser.parse(reservation["start"], dayfirst=True)
        start_time = parser.parse(reservation["end"])
        start_datetime = datetime.datetime.combine(start_date.date(), start_time.time())
        end_datetime = start_datetime + datetime.timedelta(hours=1)
        reservation["start"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        reservation["end"] = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        print("Warning: Could not convert date/time to new format. Using original values.")

print(json.dumps(reservation, indent=4))
