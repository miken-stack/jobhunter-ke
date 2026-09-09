# JobHunter KE

A job application tracker built for the Kenyan job search: log every
application, follow its status from Applied through Interview to
Offer or Rejected, and see your progress at a glance.

## Features

- Email/password authentication (Flask-Login), passwords hashed with
  Werkzeug's `generate_password_hash`
- Add, edit and delete job applications, scoped to the logged-in user
- Search by company/role, filter by status, sort by date or company
- Pagination on the dashboard
- CSRF protection on every form (Flask-WTF)
- Server-side validation (required fields, email format, password length,
  duplicate-email checks)
- Database migrations (Flask-Migrate / Alembic)
- A real test suite (pytest) covering auth, ownership checks and CRUD

## Tech stack

- Flask 3 (application factory pattern)
- Flask-SQLAlchemy (SQLite for local dev, Postgres-ready for production)
- Flask-Login, Flask-WTF, Flask-Migrate
- Vanilla CSS/JS — no frontend build step

## Project structure

```
jobhunter-ke/
├── app/
│   ├── __init__.py       # application factory
│   ├── models.py         # User, JobApplication
│   ├── forms.py          # WTForms with validation
│   ├── routes.py         # all view functions (blueprint: "main")
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
├── migrations/            # Alembic migration history
├── tests/
│   └── test_app.py
├── config.py               # Config classes (development/testing/production)
├── run.py                  # local dev entry point
├── wsgi.py                 # production entry point (gunicorn)
└── requirements.txt
```

## Getting started locally

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env and set a real SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

flask db upgrade                    # create the database tables
python run.py                       # http://127.0.0.1:5000
```

## Running tests

```bash
pytest                              # or: pytest --cov=app
```

The test suite runs against an in-memory SQLite database and never
touches your local `instance/jobhunter.db`.

## Database migrations

After changing `app/models.py`:

```bash
flask db migrate -m "Describe the change"
flask db upgrade
```

## Deployment

The app is configured for either a standard Postgres-backed host or
Vercel's serverless Python runtime (`vercel.json`).

**Important:** if deploying to Vercel (or any serverless platform), set
`DATABASE_URL` to a managed Postgres instance (e.g. Neon, Supabase, or
Vercel Postgres). Serverless filesystems are ephemeral/read-only, so
SQLite will not persist data in that environment — it's only suitable
for local development.

Required environment variables in production:

- `SECRET_KEY` — a long random value, never reused from development
- `DATABASE_URL` — a `postgresql://...` connection string
- `FLASK_CONFIG=production`

For a traditional host (Render, Railway, a VPS, etc.):

```bash
gunicorn wsgi:app
```

(a `Procfile` is included for platforms that use one).

## Security notes

- All state-changing actions (add/edit/delete, logout) require POST and
  a valid CSRF token.
- Every application route checks that the record belongs to the logged-in
  user before allowing edit/delete (returns 403 otherwise).
- Session cookies are `HttpOnly` and `SameSite=Lax`; `SESSION_COOKIE_SECURE`
  is enabled in production config (requires HTTPS).
