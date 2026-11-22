# Student Portal

A server-rendered student account application built with FastAPI, Jinja2,
SQLite + SQLAlchemy, pwdlib (Argon2) and Starlette SessionMiddleware.

## Features
- Home page with Register and Login links
- Student registration (validation, duplicate-email check, Argon2 password hash)
- Login with session (only the user ID is stored in the session)
- Protected dashboard showing name, email and role
- Admin-only page (redirects visitors who are logged out, 403 for students)
- Logout (clears the session)

## Installation

1. Clone or download the project and open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac / Linux
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Environment setup

1. Copy `.env.example` to `.env`:

   ```bash
   # Windows
   copy .env.example .env
   # Mac / Linux
   cp .env.example .env
   ```

2. Generate a secret key:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. Paste it into `.env` as the value of `SECRET_KEY`.

Never commit `.env` to Git.

## Run the application

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. The SQLite file `student_portal.db` is created automatically on first start.

## Creating an admin

Admins can't be created through the registration form. Register a normal account first, then run:

```bash
python make_admin.py your-email@example.com
```

## Project structure

| File | Purpose |
|------|---------|
| main.py | App setup, session middleware and routes |
| database.py | Database connection and `get_db` dependency |
| models.py | SQLAlchemy `User` model |
| security.py | Password hashing and verification (Argon2) |
| make_admin.py | Script that promotes a user to admin |
| templates/ | Jinja2 HTML pages |

## Notes

- `https_only=False` in the session middleware is for local HTTP development only. Use `True` when deployed behind HTTPS.
- CSRF protection is not included, as stated in the assignment. This version should not be deployed as a production authentication system without it.
- Sessions are signed cookies. Logout clears the cookie in the browser.