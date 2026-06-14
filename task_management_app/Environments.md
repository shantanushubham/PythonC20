# Environments

This project uses three environments:

| Environment | Purpose | Who uses it |
|-------------|---------|-------------|
| **Local** | Run the app on your machine while developing | Developers |
| **Dev** | Shared playground to build and test features (E2E) | Developers |
| **Prod** | Live app serving customers | Customers |

## Flow

```
Local  →  Dev  →  Prod
(you)     (team)   (customers)
```

## How it works

Settings live in `task_app/settings/`:

- `base.py` — shared config (database, Celery, logging)
- `local.py` — debug on, localhost services
- `dev.py` — debug on, remote dev host
- `prod.py` — debug off, HTTPS enforced, secrets required

Switch environments with the `APP_ENV` variable:

```bash
# Local (default)
export APP_ENV=local
python manage.py runserver

# Dev server
export APP_ENV=dev
python manage.py runserver

# Production
export APP_ENV=prod
gunicorn task_app.wsgi:application
```

You can also load env vars from a file before starting the app:

```bash
set -a && source .env.local && set +a   # Local
set -a && source .env.dev && set +a     # Dev
set -a && source .env.prod && set +a    # Prod
```

Copy the matching example file first:

```bash
cp .env.local.example .env.local
cp .env.dev.example .env.dev
cp .env.prod.example .env.prod
```

## Local setup

1. Start dependencies: `docker compose up -d`
2. Copy env file: `cp .env.local.example .env.local`
3. Run migrations: `python manage.py migrate`
4. Start the app: `python manage.py runserver`

## Environment variables

| Variable | Local | Dev | Prod |
|----------|-------|-----|------|
| `APP_ENV` | `local` | `dev` | `prod` |
| `DJANGO_SECRET_KEY` | optional | required | **required** |
| `DJANGO_ALLOWED_HOSTS` | auto | required | **required** |
| `POSTGRES_*` | localhost defaults | remote host | remote host |
| `CELERY_BROKER_URL` | localhost Redis | remote Redis | remote Redis |
| `LOG_LEVEL` | `DEBUG` | `DEBUG` | `WARNING` |

## Other environments (optional, not configured here)

Larger teams sometimes add QA, Perf, and Stage between Dev and Prod. This project starts with Local, Dev, and Prod only.
