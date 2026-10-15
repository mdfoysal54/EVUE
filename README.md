# EVU Enterprise Edition — Step 1 of 5

This is a **new isolated foundation**, not an overwrite of your existing EVU source.

## Requirements
- Docker Desktop / Docker Engine with Compose v2
- Free ports 3000 and 8000

## Installation
1. Copy `.env.example` to `.env` in this directory.
2. Replace both password and secret with independently generated random values. Example:
   `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
3. Start services: `docker compose up --build -d`
4. Create migration (initial version only): `docker compose exec backend python manage.py makemigrations catalog`
5. Apply migration: `docker compose exec backend python manage.py migrate`
6. Create admin: `docker compose exec backend python manage.py createsuperuser`
7. Open http://localhost:8000/admin/ and create a Category and Product (mark product active).
8. Open http://localhost:3000 and http://localhost:3000/shop.

**Important:** The backend container's startup migration runs before catalog's initial migration exists. After generating it, restart the backend: `docker compose restart backend`. Commit the generated `backend/catalog/migrations/0001_initial.py` into version control. Future migrations should be committed, not generated at startup.

## Verify
- `curl http://localhost:8000/api/health/`
- `curl http://localhost:8000/api/catalog/products/`
- `docker compose exec backend python manage.py check`
- `docker compose exec backend python manage.py test catalog`
- `docker compose exec frontend npm run typecheck`
- `docker compose exec frontend npm run lint`
- `docker compose exec frontend npm run build`

## Security and deployment boundaries
- This is for **local development**. The ports bind to 127.0.0.1.
- Set `DJANGO_HTTPS=true` and `DJANGO_SSL_REDIRECT=true` **only behind correctly configured HTTPS proxy**. Configure proxy SSL forwarding with an explicitly trusted proxy and test before public deployment.
- Add static-file serving, persistent secret management, HTTPS reverse proxy, structured logs, backups, CSP and rate limiting at the edge before public launch.
- Django admin is only accessible to superusers you create. Use strong passwords; MFA/admin restrictions come in Step 2.
- Image URLs entered by admins are external content; use trusted sources. Consider local/CDN uploads in Step 4.
- No payment, cart, inventory, login or customer data APIs exist in this step.
- No production security certification is claimed.

## Troubleshooting
- If the frontend starts before backend migrations, refresh after migrations.
- If you change DB credentials after volume creation, remove the volume **only if you accept data loss**; otherwise migrate credentials inside PostgreSQL.
- Inspect logs: `docker compose logs -f backend frontend db`.
- Stop: `docker compose down` (keeps DB volume).
