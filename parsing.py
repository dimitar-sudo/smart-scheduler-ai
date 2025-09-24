import spacy
import json

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
        reservation["date"] = ent.text
    elif ent.label_ == "TIME":
        reservation["time"] = ent.text

print(json.dumps(reservation, indent=2))
