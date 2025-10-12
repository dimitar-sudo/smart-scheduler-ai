from flask import Flask, render_template, request, jsonify, session
import spacy
import json
import datetime
from dateutil import parser
import re
from datetime import datetime as dt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.secret_key = os.urandom(24)

nlp = spacy.load("en_core_web_md")

excluded_names = ["the", "a", "an", "this", "that", "these", "those", 
                 "today", "tomorrow", "yesterday", "monday", "tuesday", 
                 "wednesday", "thursday", "friday", "saturday", "sunday",
                 "morning", "afternoon", "evening", "night", "pm", "am",
                 "january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"]

def is_time_expression(text):
    if not text:
        return False
    time_patterns = [
        r'^\d{1,2}\s*(?:am|pm)$',
        r'^\d{1,2}:\d{2}\s*(?:am|pm)?$',
        r'^\d{1,2}\s*(?:o\'?clock)?\s*(?:in the\s+)?(afternoon|evening|morning|night)$',
    ]
    for pattern in time_patterns:
        if re.search(pattern, str(text).lower()):
            return True
    return False

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

def get_default_reservation():
    return {
        "title": None,   
        "start": None, 
        "end": None,   
        "allDay": False,
        "description": 'Reservation made via chatbot'
    }

def safe_get(dictionary, key, default=None):
    if not isinstance(dictionary, dict):
        return default
    return dictionary.get(key, default)

def parse_reservation_text(text, current_reservation=None):
    if current_reservation is None:
        current_reservation = get_default_reservation()
    else:
        default = get_default_reservation()
        for key in default:
            if key not in current_reservation:
                current_reservation[key] = default[key]
    
    if not text or not isinstance(text, str):
        return current_reservation
    
    doc = nlp(text)
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if (ent.text.lower() not in excluded_names and 
                len(ent.text) > 1 and
                not ent.text.isdigit() and
                not any(date_word in ent.text.lower() for date_word in ["today", "tomorrow", "yesterday"]) and
                not any(day in ent.text.lower() for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) and
                not is_time_expression(ent.text)):
                current_reservation["title"] = ent.text + " Appointment"
        elif ent.label_ == "DATE":
            try:
                date_text = ent.text.lower()
                today = datetime.datetime.now()
                
                if date_text == "today":
                    current_reservation["start"] = today.strftime("%d.%m.%Y")
                elif date_text == "tomorrow":
                    tomorrow = today + datetime.timedelta(days=1)
                    current_reservation["start"] = tomorrow.strftime("%d.%m.%Y")
                elif date_text == "yesterday":
                    yesterday = today - datetime.timedelta(days=1)
                    current_reservation["start"] = yesterday.strftime("%d.%m.%Y")
                else:
                    date_text = date_text.replace("next ", "").replace("this ", "")
                    parsed_date = parser.parse(date_text, fuzzy=True)
                    current_reservation["start"] = parsed_date.strftime("%d.%m.%Y")
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
                            current_reservation["start"] = next_day.strftime("%d.%m.%Y")
                            break
                    else:
                        current_reservation["start"] = ent.text
                except:
                    current_reservation["start"] = ent.text
        elif ent.label_ == "TIME":
            time_text = ent.text
            try:
                parsed_time = parser.parse(time_text)
                current_reservation["end"] = parsed_time.strftime("%H:%M")
            except:
                current_reservation["end"] = time_text

    if not current_reservation.get("title"):
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
                    current_reservation["title"] = name_candidate + " Appointment"
                    break

    if not current_reservation.get("end") or any(word in str(current_reservation.get("end", "")).lower() for word in ["afternoon", "morning", "evening", "night"]):
        time_patterns = [
            r'(\d{1,2})\s*(?:o\'?clock)?\s*(?:in the\s+)?(afternoon|evening|morning|night)',
            r'(\d{1,2})\s*(?:o\'?clock)?\s*(am|pm)',
            r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            r'(\d{1,2})(?::(\d{2}))?\s*(?:in the\s+)?(afternoon|evening|morning|night)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minutes = 0
                if match.lastindex >= 2 and match.group(2) and match.group(2).isdigit():
                    minutes = int(match.group(2))
                period = None
                if match.lastindex >= 3 and match.group(match.lastindex):
                    period = match.group(match.lastindex).lower()
                if period in ['pm', 'afternoon', 'evening', 'night']:
                    if hour < 12:
                        hour += 12
                elif period in ['am', 'morning'] and hour == 12:
                    hour = 0
                current_reservation["end"] = f"{hour:02d}:{minutes:02d}"
                break

    if not current_reservation.get("start"):
        today = datetime.datetime.now()
        
        if re.search(r'\btoday\b', text, re.IGNORECASE):
            current_reservation["start"] = today.strftime("%d.%m.%Y")
        elif re.search(r'\btomorrow\b', text, re.IGNORECASE):
            tomorrow = today + datetime.timedelta(days=1)
            current_reservation["start"] = tomorrow.strftime("%d.%m.%Y")
        elif re.search(r'\byesterday\b', text, re.IGNORECASE):
            yesterday = today - datetime.timedelta(days=1)
            current_reservation["start"] = yesterday.strftime("%d.%m.%Y")
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
                    current_reservation["start"] = next_day.strftime("%d.%m.%Y")
            else:
                for day_name, day_num in weekday_map.items():
                    if re.search(r'\b' + day_name + r'\b', text, re.IGNORECASE):
                        days_ahead = (day_num - today.weekday() + 7) % 7
                        if days_ahead == 0:
                            current_reservation["start"] = today.strftime("%d.%m.%Y")
                        else:
                            next_day = today + datetime.timedelta(days=days_ahead)
                            current_reservation["start"] = next_day.strftime("%d.%m.%Y")
                        break

    if current_reservation.get("start") and current_reservation.get("end"):
        try:
            start_date = parser.parse(current_reservation["start"], dayfirst=True)
            time_str = current_reservation["end"]
            if ':' in time_str:
                time_parts = time_str.split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
            else:
                hours = int(time_str)
                minutes = 0
            start_datetime = datetime.datetime.combine(
                start_date.date(), 
                datetime.time(hours, minutes)
            )
            end_datetime = start_datetime + datetime.timedelta(hours=1)
            current_reservation["start"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            current_reservation["end"] = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            print(f"Error converting date/time: {e}")
            try:
                start_datetime = parser.parse(current_reservation["start"] + " " + current_reservation["end"])
                end_datetime = start_datetime + datetime.timedelta(hours=1)
                current_reservation["start"] = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                current_reservation["end"] = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                print(f"Fallback parsing also failed: {e}")

    return current_reservation

def check_overlap(new_event, existing_events):
    try:
        new_start = parser.parse(new_event["start"])
        new_end = parser.parse(new_event["end"])
        for event in existing_events:
            existing_start = parser.parse(event["start"])
            existing_end = parser.parse(event["end"])
            if (new_start < existing_end and new_end > existing_start):
                return True
        return False
    except:
        return False

@app.route('/')
def index():
    if 'reservations' not in session:
        session['reservations'] = []
    return render_template('index.html')

@app.route('/process_reservation', methods=['POST'])
def process_reservation():
    try:
        user_message = request.json.get('message', '')
        current_reservation = request.json.get('current_reservation', {})
        reservation = parse_reservation_text(user_message, current_reservation)
        response = {
            "reservation": reservation,
            "messages": [],
            "needs_info": False,
            "success": True
        }
        title = safe_get(reservation, "title")
        start_date = safe_get(reservation, "start")
        end_time = safe_get(reservation, "end")
        if end_time:
            try:
                time_obj = parser.parse(end_time).time()
                if not is_within_working_hours(time_obj):
                    response["messages"].append("The time you entered is outside working hours (09:00-17:00). Please enter a different time:")
                    response["needs_info"] = True
                    response["missing_field"] = "end"
                    reservation["end"] = None
                    return jsonify(response)
            except Exception as e:
                print(f"Time parsing error: {e}")
                response["messages"].append("Invalid time format. Please enter a valid time:")
                response["needs_info"] = True
                response["missing_field"] = "end"
                reservation["end"] = None
                return jsonify(response)
        if not title or title.lower() in excluded_names or is_time_expression(title):
            response["messages"].append("Please enter the name for the appointment:")
            response["needs_info"] = True
            response["missing_field"] = "title"
        elif not start_date:
            response["messages"].append("Please enter the date for the appointment:")
            response["needs_info"] = True
            response["missing_field"] = "start"
        elif not end_time:
            response["messages"].append("Please enter the time for the appointment:")
            response["needs_info"] = True
            response["missing_field"] = "end"
        else:
            existing_reservations = session.get('reservations', [])
            if check_overlap(reservation, existing_reservations):
                response["messages"].append("That time is already booked. Please choose a different time.")
                response["needs_info"] = True
                response["missing_field"] = "end"
                reservation["end"] = None
            else:
                existing_reservations.append(reservation)
                session['reservations'] = existing_reservations
                try:
                    start_dt = parser.parse(reservation["start"])
                    end_dt = parser.parse(reservation["end"])
                    response["messages"].append(
                        f"Appointment booked for {reservation['title']} on " +
                        f"{start_dt.strftime('%d.%m.%Y')} at {start_dt.strftime('%H:%M')}."
                    )
                    response["reservation_complete"] = True
                except Exception as e:
                    response["messages"].append(
                        f"Appointment booked for {reservation['title']}!"
                    )
                    response["reservation_complete"] = True
        if not response["messages"] and not response.get("reservation_complete"):
            response["messages"].append("I'm processing your reservation. Please provide more details if needed.")
        return jsonify(response)
    except Exception as e:
        print(f"Error in process_reservation: {e}")
        return jsonify({
            "success": False,
            "messages": ["Sorry, there was an error processing your request. Please try again."],
            "reservation": {},
            "needs_info": False
        })

@app.route('/get_reservations', methods=['GET'])
def get_reservations():
    try:
        return jsonify(session.get('reservations', []))
    except Exception as e:
        print(f"Error in get_reservations: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
