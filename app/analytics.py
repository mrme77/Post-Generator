import os
import json
from datetime import datetime

LOG_DIR = "analytics_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_analytics(event_type: str, metadata: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "metadata": metadata
    }

    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
