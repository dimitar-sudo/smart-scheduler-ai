import spacy
import json
import datetime
from dateutil import parser

nlp = spacy.load("en_core_web_md")

text = input("Enter reservation details: ")

doc = nlp(text)

reservation = {
    "name": None,
    "date": None,
    "time": None
}

for ent in doc.ents:
    if ent.label_ == "PERSON":
        reservation["name"] = ent.text
    elif ent.label_ == "DATE":
        try:
            # Parse the date and reformat to DD.MM.YYYY
            parsed_date = parser.parse(ent.text)
            reservation["date"] = parsed_date.strftime("%d.%m.%Y")
        except:
            reservation["date"] = ent.text  # Fallback to original if parsing fails
    elif ent.label_ == "TIME":
        try:
            # Parse the time and convert to 24-hour format
            parsed_time = parser.parse(ent.text)
            reservation["time"] = parsed_time.strftime("%H:%M")
        except:
            reservation["time"] = ent.text  # Fallback to original if parsing fails

print(json.dumps(reservation, indent=2))