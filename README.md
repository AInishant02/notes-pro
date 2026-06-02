# ✦ Notes Pro

A full-stack study notes manager built with Flask, SQLite, and JavaScript.

## Features

- **User Authentication** — register, login, logout with hashed passwords
- **Notes CRUD** — create, read, update, delete notes
- **Markdown Support** — format notes with headings, lists, code blocks
- **Subject Organisation** — colour-coded subjects for each note
- **Tags** — comma-separated tags per note
- **File Attachments** — upload PDFs and images
- **Full-Text Search** — search by title, content, or filter by subject
- **Public Share Links** — share any note via a unique URL
- **AI Assistant** — summarise notes, generate quizzes & flashcards (Gemini API)
- **Dark/Light Mode** — toggle with the floating button
- **Responsive UI** — works on mobile and desktop

---

## Quick Start

### 1. Clone / unzip the project

```bash
cd notes-pro
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY and optionally GEMINI_API_KEY
```

### 5. Run the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

---

## AI Features (Optional)

Set `GEMINI_API_KEY` in your `.env` to enable:
- **Summarise** — bullet-point summary of note content
- **Quiz Me** — 5 multiple-choice questions
- **Flashcards** — 8 Q&A flashcard pairs

Get a free key at https://ai.google.dev/

---

## Deployment (Render)

1. Push to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables: `SECRET_KEY`, `DATABASE_URL` (PostgreSQL), `GEMINI_API_KEY`

---

## Project Structure

```
notes-pro/
├── app.py                  # Main Flask app & all routes
├── requirements.txt
├── Procfile                # For deployment
├── .env.example
├── models/
│   └── models.py           # SQLAlchemy models (User, Note, Subject, Tag)
├── static/
│   ├── css/style.css       # All styles (dark/light theme)
│   ├── js/script.js        # Theme toggle, sidebar, flash dismiss
│   └── uploads/            # User-uploaded files
└── templates/
    ├── base.html            # Layout with sidebar
    ├── index.html           # Landing page
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── create_note.html     # Markdown editor
    ├── edit_note.html
    ├── view_note.html       # Rendered markdown + AI panel
    ├── subjects.html
    └── search.html
```

---

## Database Schema

**users**: id, username, email, password, created_at  
**notes**: id, title, content, subject_id, file_path, user_id, is_public, share_token, created_at, updated_at  
**subjects**: id, name, color, user_id, created_at  
**tags**: id, name, user_id  
**note_tags**: note_id, tag_id (many-to-many)

---

## Resume Description

> Built a full-stack Study Notes Manager using Flask, SQLAlchemy, SQLite/PostgreSQL, and vanilla JavaScript with user authentication, file uploads, full-text search, Markdown rendering, and Gemini AI integration for note summarisation, quiz generation, and flashcard creation. Deployed on Render with PostgreSQL.
