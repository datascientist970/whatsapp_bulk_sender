# WhatsApp Business Suite — Bulk Messaging Platform with AI Message Generation

> A Django web application for WhatsApp bulk messaging: validate numbers, generate marketing messages with AI (Groq), and send campaigns through WhatsApp Web — with delivery tracking from a single dashboard.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Django](https://img.shields.io/badge/Django-5.0.2-green)
![Groq](https://img.shields.io/badge/AI-Groq-orange)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)

## Overview

WhatsApp Business Suite is built for businesses that communicate with customers on WhatsApp: marketing campaigns, notifications, reminders, and announcements. It pairs a Selenium-based WhatsApp Web sending engine (`whatsapp_sender/whatsapp_handler.py`) with an AI handler (`whatsapp_sender/ai_handler.py`) powered by the Groq API, so messages can be generated in different tones instead of written one by one.

## Key Features

- **Bulk sending** — send a message to many recipients in one campaign
- **AI message generator** — generate professional marketing messages with the Groq API, in multiple tones
- **Multi-send** — optionally send the same message multiple times per recipient (configurable, up to 50)
- **Number validation** — check which numbers are on WhatsApp before sending
- **Real-time tracking** — monitor delivery status and campaign success rates as sending progresses
- **Secure session handling** — managed WhatsApp Web session via Selenium + webdriver-manager

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0.2 (Python) |
| AI | Groq API (`groq` Python SDK) |
| Automation | Selenium 4.18, webdriver-manager (WhatsApp Web) |
| Config | python-dotenv (`.env` for API keys) |
| Database | SQLite |
| Frontend | Django templates (HTML/CSS/JavaScript) |
| Other | requests, httpx, django-cors-headers |

## Project Structure

```
├── whatsapp_bulk_sender/   # Project settings & URLs
├── whatsapp_sender/
│   ├── ai_handler.py        # Groq-powered AI message generation
│   ├── whatsapp_handler.py  # Selenium WhatsApp Web sending engine
│   ├── models.py / views.py / urls.py
│   └── templates/core/index.html
├── requirements.txt
├── install.bat              # Windows one-click installer
├── .env                     # API keys (create your own — never commit real keys)
└── manage.py
```

## Getting Started

```bash
git clone https://github.com/datascientist970/whatsapp_bulk_sender.git
cd whatsapp_bulk_sender

python -m venv venv
venv\Scripts\activate        # Windows — or simply run install.bat
pip install -r requirements.txt
```

Create your `.env` file with your own Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Then:

```bash
python manage.py migrate
python manage.py runserver
```

## Usage

1. Open the app in your browser and connect WhatsApp by scanning the WhatsApp Web QR code when the sender starts.
2. Add/import recipient numbers and (optionally) validate them.
3. Write a message yourself — or let the AI generator draft one in the tone you want.
4. Choose the send count per recipient, start the campaign, and watch delivery status update in real time.

> Use bulk messaging responsibly and only with recipients who have opted in; unsolicited bulk messaging can get a WhatsApp number restricted.

## Author

**Muhammad Dawood** — AI & Data Science Engineer
GitHub: https://github.com/datascientist970 · Mardan, Pakistan
