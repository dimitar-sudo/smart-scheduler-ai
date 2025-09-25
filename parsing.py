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

# Extract entities
for ent in doc.ents:
    if ent.label_ == "PERSON":
        reservation["name"] = ent.text
    elif ent.label_ == "DATE":
        try:
            # Clean the date text and parse
            date_text = ent.text.lower().replace("next ", "").replace("this ", "")
            parsed_date = parser.parse(date_text, fuzzy=True)
            reservation["date"] = parsed_date.strftime("%d.%m.%Y")
        except:
            # Try to handle relative dates like "next monday"
            try:
                today = datetime.datetime.now()
                if "monday" in ent.text.lower():
                    days_ahead = (0 - today.weekday() + 7) % 7
                    if days_ahead == 0:  # Today is Monday
                        days_ahead = 7
                    next_monday = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_monday.strftime("%d.%m.%Y")
                elif "tuesday" in ent.text.lower():
                    days_ahead = (1 - today.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                elif "wednesday" in ent.text.lower():
                    days_ahead = (2 - today.weekdown() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                elif "thursday" in ent.text.lower():
                    days_ahead = (3 - today.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                elif "friday" in ent.text.lower():
                    days_ahead = (4 - today.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                elif "saturday" in ent.text.lower():
                    days_ahead = (5 - today.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                elif "sunday" in ent.text.lower():
                    days_ahead = (6 - today.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    next_day = today + datetime.timedelta(days=days_ahead)
                    reservation["date"] = next_day.strftime("%d.%m.%Y")
                else:
                    reservation["date"] = ent.text
            except:
                reservation["date"] = ent.text
    elif ent.label_ == "TIME":
        # Clean the time text - take only the time part before any other words
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', ent.text, re.IGNORECASE)
        if time_match:
            time_text = time_match.group(1)
            try:
                parsed_time = parser.parse(time_text)
                reservation["time"] = parsed_time.strftime("%H:%M")
            except:
                reservation["time"] = time_text
        else:
            reservation["time"] = ent.text

# Fallback: if entities weren't properly detected, use pattern matching
if not reservation["name"]:
    # Look for name after "under", "for", or "name"
    name_patterns = [
        r"under\s+(\w+)",
        r"for\s+(\w+)$",
        r"name\s+(\w+)",
        r"under\s+the\s+name\s+(\w+)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reservation["name"] = match.group(1)
            break

if not reservation["time"]:
    # Look for time patterns in the text
    time_pattern = r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))'
    match = re.search(time_pattern, text, re.IGNORECASE)
    if match:
        time_text = match.group(1)
        try:
            parsed_time = parser.parse(time_text)
            reservation["time"] = parsed_time.strftime("%H:%M")
        except:
            reservation["time"] = time_text

if not reservation["date"]:
    # Look for date patterns or relative dates
    date_pattern = r'(\d{4}[.-]\d{1,2}[.-]\d{1,2})|(next\s+\w+)'
    match = re.search(date_pattern, text, re.IGNORECASE)
    if match:
        date_text = match.group(0)
        try:
            parsed_date = parser.parse(date_text, fuzzy=True)
            reservation["date"] = parsed_date.strftime("%d.%m.%Y")
        except:
            reservation["date"] = date_text

print(json.dumps(reservation, indent=2))