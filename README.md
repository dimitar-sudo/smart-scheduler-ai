# 🗓️ Smart Scheduler AI — Conversational Appointment Scheduler

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://smart-scheduler-ai.onrender.com)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)  
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green)](https://flask.palletsprojects.com)  
[![spaCy](https://img.shields.io/badge/spaCy-3.8.7-purple)](https://spacy.io)

A professional, dark-themed web application that demonstrates conversational NLP-driven scheduling. Users can create appointments via a chat interface; the backend extracts names, dates and times with spaCy and renders events on a FullCalendar UI.

![Smart Scheduler Interface](screenshot.png)

---

## Features

- **🗣️ Natural-language Booking**: Parse user messages into appointment data (name, date, time).  
- **📅 FullCalendar Integration**: Events appear on a responsive calendar.  
- **⚠️ Conflict Detection**: Overlap checking to avoid double-booking.  
- **🧭 Robust Date/Time Handling**: Uses python-dateutil with multiple parsing fallbacks and heuristics.  
- **💬 Chat-style UX**: Progressive information requests when details are missing (name/date/time).  
- **🎨 Polished UI**: Dark theme, responsive layout, accessible components.

---

## Technologies Used

- Backend: Python (3.11/3.12 recommended), Flask  
- NLP: spaCy (en_core_web_md)  
- Date/time parsing: python-dateutil  
- Frontend: HTML, CSS, Vanilla JavaScript, FullCalendar  
- Session handling: Flask-Session (session-backed reservations)  

---

## Project Structure

```
smart-scheduler-ai/
├── app.py                     # Flask app + NLP parsing & routing
├── requirements.txt           # Python dependencies (see below)
├── templates/
│   └── index.html             # Main UI template (calendar + chat)
├── static/
│   ├── style.css              # UI styles (dark theme)
│   └── script.js              # ReservationChatbot client-side class
├── README.md                  # This file
└── LICENSE                    # (optional) MIT license recommended
```

---

## Quickstart (Local)

1. Create and activate a virtualenv:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
If the spaCy model wheel from requirements fails, install the model manually:
```bash
python -m spacy download en_core_web_md
```

3. Run the app locally:
```bash
python app.py
```
Open http://127.0.0.1:5000

For production: run with Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

---

## How it works — Key Flows

### Booking flow
1. User types a natural-language request (e.g., "Book a meeting with Sarah tomorrow at 3pm").  
2. Backend (spaCy + heuristics) extracts PERSON, DATE, TIME and normalizes into a reservation object.  
3. If data is missing, the bot prompts for the missing field(s).  
4. Once complete, the reservation object is stored in session and rendered on FullCalendar.  
5. Overlap detection prevents double-booking and triggers conflict responses.

### Main code areas to review
- app.py — parsing logic (parse_reservation_text), overlap checking (check_overlap), endpoints (/process_reservation, /get_reservations)  
- static/script.js — frontend chatbot flow (ReservationChatbot), calendar event mapping  
- static/style.css — UI styling and responsive layout

---

## Technical highlights 

- SpaCy NER combined with custom regex fallbacks for robust, real-world parsing.  
- Progressive form filling via conversational UX.  
- Session-based storage for quick demos; easy to upgrade to DB (SQLite/Postgres) for persistence.  
- Clean separation of concerns: parsing + validation (backend) vs rendering + UX (frontend).  

---

## Future enhancements

- [ ] Persist reservations in a database (SQLite / Postgres) and add user accounts  
- [ ] Add timezone support and user-localized formatting  
- [ ] Improve NER via spaCy custom components / rule-based matchers  
- [ ] Add unit tests around parsing edge cases and overlap detection  
- [ ] Dockerfile + CI pipeline + Render/Heroku deployment example  
- [ ] Export calendar to .ics and calendar invite emails

---

## License

This project is licensed under the MIT License — meaning you're free to use, modify, and distribute it with attribution.  
See [LICENSE](LICENSE) for full terms.

---

**Developed by Dimitar Karaskakovski**  
[GitHub Portfolio](https://github.com/dimitar-sudo)
