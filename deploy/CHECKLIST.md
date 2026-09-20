# Production Deployment Checklist

## Security
- [ ] Ensure `.env` is omitted from Version Control (`.gitignore`).
- [ ] `FLASK_ENV` is set to `production`.
- [ ] `SECRET_KEY` is a highly secure, random 64-character string.
- [ ] Application is running behind HTTPS / SSL via Nginx/Certbot.
- [ ] Check `WTF_CSRF_ENABLED` is `True`.
- [ ] Redis is installed and running if scaling Rate Limiters and Cache.

## Database
- [ ] Run database backups before any migrations.
- [ ] Default Admin password has been changed via the Dashboard.
- [ ] Database indexes have successfully migrated.

## Monitoring & Queues
- [ ] APScheduler is successfully triggering background threads (Verify via `/system/queue`).
- [ ] Check disk space on deployment server (Verify via `/system/health`).
- [ ] Verify directory permissions for `/static/uploads` and `/logs`.

## Performance
- [ ] Confirm Gunicorn is configured with at least `(2 x core_count) + 1` workers.
- [ ] Static files are being served directly by Nginx rather than Flask.