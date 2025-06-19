import os
import json
from datetime import datetime
from difflib import SequenceMatcher

LOG_DIR = "analytics_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_analytics(event_type: str, metadata: dict, content: str = None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "metadata": metadata
    }
    if content:
        entry["content"] = content

    log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


MAX_HISTORY = 10

def get_recent_generated_posts() -> list:
    posts = []
    for filename in sorted(os.listdir(LOG_DIR), reverse=True):
        if not filename.endswith(".jsonl"):
            continue
        path = os.path.join(LOG_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            for line in reversed(list(f)):
                try:
                    data = json.loads(line.strip())
                    if data.get("event_type") == "generation" and "content" in data:
                        posts.append(data["content"])
                        if len(posts) >= MAX_HISTORY:
                            return posts
                except json.JSONDecodeError:
                    continue
    return posts

def is_too_similar(new_post: str, threshold: float = 0.85) -> bool:
    recent_posts = get_recent_generated_posts()
    for post in recent_posts:
        similarity = SequenceMatcher(None, new_post, post).ratio()
        if similarity > threshold:
            return True
    return False
