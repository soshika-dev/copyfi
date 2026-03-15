# PasteHub Backend (Flask + PostgreSQL)

Production-ready REST API for a pastebin-style app with anonymous pastes, optional accounts, private/unlisted visibility, TTL expiry, password-protected pastes, abuse reports, moderation, tags, and collections.

## Stack
- Python 3.12+
- Flask app factory (`create_app`)
- SQLAlchemy 2.x + Flask-Migrate/Alembic
- PostgreSQL (primary), SQLite (tests)
- JWT access + refresh tokens
- Pydantic v2 validation
- Flask-Limiter rate limiting (Redis-backed in Docker)
- pytest + pytest-flask

## Features
- Anonymous and authenticated paste creation
- Visibility model:
  - `public`: anyone with slug
  - `unlisted`: link-only (never globally listed)
  - `private`: owner/admin only
- Expiration options: `10m`, `1h`, `1d`, `1w`, `1m`, `never`
- Password-protected pastes (`X-Paste-Password` header on read)
- File paste uploads (zip/pdf/doc/docx/xls/xlsx/ppt/pptx/csv/txt/json)
- Burn-after-read support
- Tag support
- Owner collections/folders
- Abuse reporting and admin moderation
- JSON error format:
  ```json
  {
    "error": {
      "code": "...",
      "message": "...",
      "details": {}
    }
  }
  ```

## Project Layout
```text
backend/
  app/
    __init__.py
    commands.py
    config.py
    extensions.py
    api/v1/
    models/
    schemas/
    services/
    utils/
  migrations/
  tests/
  docker/Dockerfile
  docker-compose.yml
  requirements.txt
  openapi.yaml
  .env.example
```

## Quick Start (Local)
1. Create env file:
   ```bash
   cd backend
   cp .env.example .env
   ```
   `.env.example` is set for local (non-Docker) development (`localhost` DB host).
2. Install dependencies:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Export Flask app:
   ```bash
   export FLASK_APP=wsgi:app
   export FLASK_ENV=development
   ```
4. Run migrations:
   ```bash
   flask db upgrade
   ```
5. Start API:
   ```bash
   flask run --host 0.0.0.0 --port 5001
   ```

## Docker
```bash
cd backend
cp .env.example .env
docker compose up --build
```

This starts:
- API: `http://localhost:5001`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Migrations
```bash
cd backend
export FLASK_APP=wsgi:app
flask db upgrade
# create new migration
flask db migrate -m "message"
flask db upgrade
```

## Cleanup Job
Expired/soft-deleted records are removed via CLI command:
```bash
flask clean-expired
```
Example cron (every 15 minutes):
```cron
*/15 * * * * cd /path/to/repo/backend && /path/to/venv/bin/flask clean-expired
```

Promote an existing user to admin:
```bash
flask make-admin <username>
```

## Tests
```bash
cd backend
pytest
```

## Security Controls
- Password hashing via `passlib` (`pbkdf2_sha256`)
- Secure random non-sequential slugs
- Content size cap enforced server-side (`MAX_PASTE_BYTES`, default 512KB)
- File size cap enforced server-side (`MAX_FILE_BYTES`, default 20MB)
- Input validation with Pydantic v2
- Rate limiting on auth/paste/report endpoints
- Private paste access checks (owner/admin only)
- Password-protected paste reads require `X-Paste-Password`

## API Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

### Pastes
- `POST /api/v1/pastes`
- `POST /api/v1/pastes/file` (multipart file upload)
- `GET /api/v1/pastes/{slug}`
- `GET /api/v1/pastes/{slug}/raw`
- `GET /api/v1/pastes/{slug}/download`
- `PATCH /api/v1/pastes/{slug}`
- `PUT /api/v1/pastes/{slug}`
- `DELETE /api/v1/pastes/{slug}`
- `POST /api/v1/pastes/{slug}/report`

### Me
- `GET /api/v1/me/pastes`
- `GET /api/v1/me/collections`
- `POST /api/v1/me/collections`
- `DELETE /api/v1/me/collections/{collection_id}`

### Admin
- `GET /api/v1/admin/reports`
- `PATCH /api/v1/admin/reports/{id}`
- `DELETE /api/v1/admin/pastes/{slug}`
- `PATCH /api/v1/admin/users/{id}/ban`

## cURL Examples

Register:
```bash
curl -X POST http://localhost:5001/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"Secret123","email":"alice@example.com"}'
```

Login:
```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"Secret123"}'
```

Create paste (anonymous):
```bash
curl -X POST http://localhost:5001/api/v1/pastes \
  -H 'Content-Type: application/json' \
  -d '{"content":"print(1)","language":"python","visibility":"unlisted","expires_in":"1d","tags":["python"]}'
```

Create private paste (authenticated):
```bash
curl -X POST http://localhost:5001/api/v1/pastes \
  -H "Authorization: Bearer <access-token>" \
  -H 'Content-Type: application/json' \
  -d '{"content":"secret","visibility":"private"}'
```

Create file paste (anonymous):
```bash
curl -X POST http://localhost:5001/api/v1/pastes/file \
  -F "file=@/path/to/report.pdf" \
  -F "visibility=unlisted" \
  -F "expires_in=1d" \
  -F "tags=docs,pdf"
```

Download file paste:
```bash
curl -L http://localhost:5001/api/v1/pastes/<slug>/download -o downloaded-file
```

Read password-protected paste:
```bash
curl http://localhost:5001/api/v1/pastes/<slug> \
  -H 'X-Paste-Password: mypass'
```

List my pastes:
```bash
curl "http://localhost:5001/api/v1/me/pastes?page=1&limit=20" \
  -H "Authorization: Bearer <access-token>"
```

Report paste:
```bash
curl -X POST http://localhost:5001/api/v1/pastes/<slug>/report \
  -H 'Content-Type: application/json' \
  -d '{"reason":"Malicious content"}'
```

Admin ban user:
```bash
curl -X PATCH http://localhost:5001/api/v1/admin/users/<user-id>/ban \
  -H "Authorization: Bearer <admin-access-token>" \
  -H 'Content-Type: application/json' \
  -d '{"is_banned": true}'
```
