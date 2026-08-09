# NITEANKH (Python/Flask)

Dynamic rebuild of the niteankhv2 static mockup — real database, real accounts, real
file-based video/thumbnail uploads, server-rendered pages.

## Stack

- Flask + Flask-SQLAlchemy (SQLite, file `niteankh.db`)
- Server-rendered Jinja2 templates (same Tailwind CDN + gold/dark theme as the original)
- Session-based auth (Werkzeug password hashing, no third-party auth library)
- Uploaded videos/thumbnails stored under `static/uploads/` and served by Flask's
  static handler (supports HTTP Range requests, so `<video>` seeking works)

## Setup

```bash
cd "C:\all py\niteankh"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py     # creates niteankh.db, seeds 120 movies + demo accounts
python app.py       # runs on http://127.0.0.1:5000
```

## Demo accounts

| Role  | Email                  | Password  |
|-------|------------------------|-----------|
| Admin | admin@niteankh.local   | admin123  |
| User  | demo@niteankh.local    | demo1234 (starts with 1000 coins) |

Admin panel: http://127.0.0.1:5000/admin/login

## Project layout

```
app.py          Flask app factory + public routes (home, movies, search, watch,
                 membership, wallet, profile, login/signup)
admin.py        Admin blueprint (/admin/...) — dashboard, upload, manage, reports
models.py       SQLAlchemy models: User, Movie, WalletTransaction, MyListItem, HistoryItem
helpers.py      Shared constants + auth decorators (login_required, admin_required)
seed.py         One-time DB seed (120 mock movies + admin/demo accounts)
templates/      Jinja2 templates (base.html + per-page, admin/ subfolder for admin)
static/uploads/ Uploaded video/thumbnail files land here
niteankh.db     SQLite database (created by seed.py)
```

## What's real now (vs. the static mockup)

- Accounts, passwords, sessions — real, server-side, shared across devices
- Wallet balance / VIP status / transaction history — real, per-account, in the database
- My List / watch history — real, per-account, in the database
- Admin-uploaded videos/thumbnails — real files on disk, served to any visitor
  (not just the browser that uploaded them, unlike the old IndexedDB version)
- Admin reports — real SQL aggregates across all registered accounts

## Known limitations (still true, worth knowing)

- **Dev server only.** `python app.py` runs Flask's built-in dev server — fine for
  local use, not for production traffic. For real deployment you'd run it behind
  a WSGI server (gunicorn/waitress) and a reverse proxy.
- **SQLite + local disk storage.** Works great for one machine; doesn't scale to
  multiple servers without moving to Postgres + object storage (e.g. S3/R2) for uploads.
  This is exactly what we discussed for a Cloudflare deployment path.
- **Tailwind via CDN.** Same as the static version — fine for this scope, not ideal
  for a production build (no purge/minify).
- **Google/Telegram login buttons are still non-functional placeholders** — real OAuth
  needs registered app credentials with each provider, a separate integration.
- **`SECRET_KEY` defaults to a dev value.** Set the `SECRET_KEY` environment variable
  before deploying anywhere real.
