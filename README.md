# WhatsApp CRM

> A full-stack WhatsApp CRM built with Python Flask for managing customers, campaigns, messaging, templates, media, automation, and Instagram integrations from one dashboard.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Integration-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://www.whatsapp.com/)
[![Instagram](https://img.shields.io/badge/Instagram-Integration-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](#license)

---

## Overview

WhatsApp CRM is a web-based customer relationship management platform designed to help businesses manage customer data, WhatsApp campaigns, message templates, media, automation workflows, and social integrations from a centralized dashboard.

The project is built with **Python + Flask** and follows a modular architecture with separate layers for routes, services, models, forms, utilities, and database management.

---

## Features

### CRM

- Customer management
- Customer import from CSV
- Customer search and filtering
- Customer profiles
- Lead management
- Customer activity tracking
- Dashboard statistics

### WhatsApp

- WhatsApp messaging integration
- Campaign management
- Message templates
- Campaign history
- Campaign logs
- Automated messaging workflows
- Message scheduling
- Notification services
- WhatsApp service layer

### Instagram

- Instagram account management
- Instagram integration
- Instagram token management
- Instagram content management
- Account status tracking
- Profile information storage

### Campaign Management

- Create campaigns
- Edit campaigns
- View campaign details
- Campaign history
- Campaign logs
- Customer targeting
- Automated campaign execution

### Media Management

- Media upload
- Media library
- Media management
- File metadata
- Campaign media support

### Automation

- Scheduled tasks
- Automation services
- Background workflows
- Campaign automation
- Customer follow-ups
- Notification handling

### Authentication & Security

- User authentication
- Login system
- Form validation
- Authentication services
- Protected routes
- Session management
- Audit logging
- Environment-based configuration

### Dashboard

- CRM overview
- Campaign statistics
- Customer statistics
- Analytics
- Activity information
- System information

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python |
| Framework | Flask |
| ORM | SQLAlchemy |
| Frontend | HTML5, CSS3, JavaScript |
| UI | Bootstrap 5 |
| Database | SQLAlchemy-compatible database |
| Forms | Flask-WTF |
| Authentication | Flask-Login |
| Data Processing | Pandas |
| Excel/CSV | OpenPyXL |
| API Communication | Requests |
| Production Server | Gunicorn |
| Reverse Proxy | Nginx |
| Environment | Python `.env` configuration |

---

## Project Architecture

```text
whatsapp-crm/
│
├── app.py
├── config.py
├── wsgi.py
├── requirements.txt
├── .env.example
├── .gitignore
├── TODO.md
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── deploy/
│   ├── CHECKLIST.md
│   ├── DEPLOYMENT.md
│   ├── gunicorn_config.py
│   ├── nginx.conf
│   └── systemd.service
│
├── forms/
│   ├── campaign_form.py
│   ├── customer_form.py
│   ├── instagram_forms.py
│   ├── login_form.py
│   ├── settings_form.py
│   └── template_form.py
│
├── models/
│   ├── admin.py
│   ├── campaign.py
│   ├── campaign_log.py
│   ├── customer.py
│   ├── instagram.py
│   ├── media_file.py
│   ├── message_template.py
│   ├── settings.py
│   └── system.py
│
├── routes/
│   ├── auth.py
│   ├── campaigns.py
│   ├── customers.py
│   ├── dashboard.py
│   ├── instagram.py
│   ├── media.py
│   ├── settings.py
│   ├── system.py
│   └── templates.py
│
├── services/
│   ├── analytics_service.py
│   ├── audit_service.py
│   ├── auth_service.py
│   ├── automation_service.py
│   ├── backup_service.py
│   ├── campaign_service.py
│   ├── content_generator_service.py
│   ├── csv_import.py
│   ├── customer_service.py
│   ├── dashboard_service.py
│   ├── instagram_service.py
│   ├── instagram_token_service.py
│   ├── lead_service.py
│   ├── media_service.py
│   ├── notification_service.py
│   ├── scheduler_service.py
│   ├── template_service.py
│   └── whatsapp.py
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── auth/
│   ├── campaigns/
│   ├── customers/
│   ├── dashboard/
│   ├── errors/
│   ├── media/
│   ├── partials/
│   ├── settings/
│   └── templates/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_campaigns.py
│   ├── test_customers.py
│   ├── test_models.py
│   └── test_whatsapp.py
│
└── utils/
    ├── constants.py
    ├── decorators.py
    ├── helpers.py
    └── validators.py
