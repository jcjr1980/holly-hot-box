"""
Gunicorn configuration for Holly Hot Box
"""
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Worker processes
workers = 2
worker_class = 'sync'

# Timeout - 10 MINUTES for complex LLM queries
timeout = 600
graceful_timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'holly_hot_box'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

