import multiprocessing
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")

# Recommended formula: (2 x $num_cores) + 1
default_workers = multiprocessing.cpu_count() * 2 + 1
workers = int(os.getenv("GUNICORN_WORKERS", min(default_workers, 8)))

# Thread concurrency per worker
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = "gthread"

# Timeout & Keepalive
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'
