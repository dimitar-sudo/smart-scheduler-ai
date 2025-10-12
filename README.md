# Smart Scheduler AI — Appointment Chatbot

A polished, dark-themed web app that parses natural-language appointment requests and schedules events on a FullCalendar UI. Designed for portfolio presentation to demonstrate practical skills in Python, NLP (spaCy), Flask, and frontend integration.

Quick links
- Code: [app.py](app.py)
- Frontend: [templates/index.html](templates/index.html)
- Client script: [static/script.js](static/script.js) (class: [`ReservationChatbot`](static/script.js))
- Styles: [static/style.css](static/style.css)
- Requirements: [requirements.txt](requirements.txt)

Highlights
- Natural language parsing using spaCy to extract names, dates and times (see [`app.parse_reservation_text`](app.py)).
- Robust date/time handling with python-dateutil and fallback heuristics.
- Conflict detection via [`app.check_overlap`](app.py).
- Working-hours validation via [`app.is_within_working_hours`](app.py) and time-expression detection via [`app.is_time_expression`](app.py).
- Clean, responsive UI with FullCalendar and a chat-style assistant (see [`ReservationChatbot`](static/script.js)).

Features
- Conversational booking flow with progressive information requests.
- Automatic parsing of PERSON, DATE, and TIME entities and multiple fallbacks.
- Session-based reservation storage and calendar rendering.
- Accessible, modern UI with a dark theme and event color-coding.

Tech stack
- Python 3.10+ (Flask backend)
- spaCy (NLP) + en_core_web_md model
- python-dateutil for robust parsing
- FullCalendar (CDN) for calendar UI
- Vanilla JS for chatbot UI

Install & run (local development)
1. Create a virtual environment and activate:
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows