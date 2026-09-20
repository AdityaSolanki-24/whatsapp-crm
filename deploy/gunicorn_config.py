"""
Gunicorn production configuration for WhatsApp CRM.
Usage: gunicorn -c deploy/gunicorn_config.py wsgi:app
"""
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300          # Long timeout for campaign sends
keepalive = 5

# Restart workers after this many requests (memory leak guard)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog  = "logs/gunicorn_error.log"
loglevel  = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# Process naming
proc_name = "whatsapp_crm"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for faster worker boot
preload_app = True

def on_starting(server):
    os.makedirs("logs", exist_ok=True)

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited")
