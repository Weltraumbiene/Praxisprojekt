#/backend/app/logs.py
from threading import Lock

log_buffer = []
log_lock = Lock()

def log_message(msg: str):
    print(msg)
    with log_lock:
        log_buffer.append(msg)
        if len(log_buffer) > 300:
            log_buffer.pop(0)

def get_log_buffer():
    with log_lock:
        return list(log_buffer) 
