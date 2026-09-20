# WhatsApp CRM — Ubuntu Deployment Guide

## Prerequisites

- Ubuntu 22.04 LTS (or 20.04)
- Python 3.12
- MySQL 8.0
- Nginx
- Domain name (for SSL)
- WhatsApp Business API credentials from Meta for Developers

---

## 1. Server Preparation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    build-essential git nginx \
    mysql-server libmysqlclient-dev pkg-config
```

---

## 2. MySQL Setup

```bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

Inside MySQL:

```sql
CREATE DATABASE whatsapp_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crm_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON whatsapp_crm.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 3. Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/whatsapp_crm
sudo chown $USER:$USER /var/www/whatsapp_crm

# Clone / upload your project
cd /var/www
git clone https://your-repo-url.git whatsapp_crm
# OR upload via scp / rsync

cd /var/www/whatsapp_crm

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Environment Configuration

```bash
cp .env.example .env
nano .env
```

Fill in all values:

```
FLASK_ENV=production
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=mysql+pymysql://crm_user:YourStrongPassword123!@localhost/whatsapp_crm
WHATSAPP_PHONE_ID=<your_phone_number_id>
WHATSAPP_ACCESS_TOKEN=<your_access_token>
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

---

## 5. Database Initialisation

```bash
cd /var/www/whatsapp_crm
source venv/bin/activate

# Tables are created automatically on first run
python wsgi.py  # test once, then Ctrl+C
```

This creates:
- All database tables
- Default admin: `admin` / `admin123` (change immediately!)
- Default message templates

---

## 6. Folder Permissions

```bash
sudo chown -R www-data:www-data /var/www/whatsapp_crm
sudo chmod -R 755 /var/www/whatsapp_crm
sudo chmod -R 775 /var/www/whatsapp_crm/static/uploads
sudo chmod -R 775 /var/www/whatsapp_crm/logs
```

---

## 7. Systemd Service

```bash
sudo cp deploy/systemd.service /etc/systemd/system/whatsapp_crm.service
# Edit paths if your app is not at /var/www/whatsapp_crm
sudo nano /etc/systemd/system/whatsapp_crm.service

sudo systemctl daemon-reload
sudo systemctl enable whatsapp_crm
sudo systemctl start whatsapp_crm
sudo systemctl status whatsapp_crm
```

Check logs:
```bash
sudo journalctl -u whatsapp_crm -f
tail -f /var/www/whatsapp_crm/logs/gunicorn_error.log
```

---

## 8. Nginx Configuration

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/whatsapp_crm

# Edit your domain name
sudo nano /etc/nginx/sites-available/whatsapp_crm

# Enable site
sudo ln -s /etc/nginx/sites-available/whatsapp_crm /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reload
sudo systemctl restart nginx
```

---

## 9. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo certbot renew --dry-run
```

---

## 10. First Login & Security Steps

1. Open `https://your-domain.com`
2. Login with `admin` / `admin123`
3. **Immediately change the password** (Settings page or recreate via DB)
4. Go to **Settings** → enter WhatsApp Phone ID and Access Token
5. Click **Test Connection** to verify

---

## 11. Maintenance Commands

```bash
# Restart application
sudo systemctl restart whatsapp_crm

# View live logs
sudo journalctl -u whatsapp_crm -f

# Reload nginx
sudo systemctl reload nginx

# Update application
cd /var/www/whatsapp_crm
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart whatsapp_crm
```

---

## 12. WhatsApp API Setup Reference

1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create App → Business type
3. Add **WhatsApp** product
4. Navigate to **WhatsApp → API Setup**
5. Add a test recipient phone number
6. Copy **Phone Number ID** → paste in CRM Settings
7. Generate **Temporary Access Token** (or set up permanent one)
8. Paste in CRM Settings → Test Connection

### Permanent Token (Production)

For production, create a **System User** in Meta Business Suite:
1. Business Settings → System Users → Add
2. Assign WhatsApp permissions
3. Generate token with `whatsapp_business_messaging` scope
4. This token does not expire

---

## 13. CSV Import Format

```csv
customer_id,name,email,phone,orders,status
CUST001,Rahul Sharma,rahul@email.com,919876543210,5,active
CUST002,Priya Patel,,917654321098,2,active
CUST003,Amit Kumar,amit@gmail.com,918765432109,0,inactive
```

**Rules:**
- Phone must include country code (no `+`, no spaces)
- Duplicate phones are skipped automatically
- Status: `active`, `inactive`, or `blocked`
- Only `active` customers receive campaign messages

---

## 14. Running Tests

```bash
cd /var/www/whatsapp_crm
source venv/bin/activate
pip install pytest
pytest tests/ -v
```

---

## 15. Backup Strategy

```bash
# Database backup (daily cron)
mysqldump -u crm_user -p whatsapp_crm > /backups/whatsapp_crm_$(date +%Y%m%d).sql

# Media backup
rsync -av /var/www/whatsapp_crm/static/uploads/ /backups/uploads/

# Cron job (/etc/cron.d/whatsapp_crm)
0 2 * * * www-data mysqldump -u crm_user -pYourPassword whatsapp_crm > /backups/db_$(date +\%Y\%m\%d).sql
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check `sudo systemctl status whatsapp_crm` |
| DB Connection Error | Verify `.env` DATABASE_URL and MySQL is running |
| File Upload Fails | Check `/static/uploads/` permissions (www-data writable) |
| WhatsApp API 401 | Access token expired — regenerate in Meta Developer Console |
| WhatsApp API 400 | Invalid phone format — ensure no `+` or spaces, include country code |
| Campaign stuck "running" | Server restarted mid-send; manually set status to `completed` in DB |
