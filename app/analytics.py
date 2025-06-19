import json
from datetime import datetime
from difflib import SequenceMatcher
from google.cloud import storage
from google.oauth2 import service_account
import os

# CONFIG
BUCKET_NAME = "post_generator1"
LOG_DIR = "analytics_logs"
MAX_HISTORY = 10

# Load credentials if GOOGLE_APPLICATION_CREDENTIALS contains JSON content
gcp_creds_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

if gcp_creds_env and gcp_creds_env.strip().startswith('{'):
    # It's raw JSON content from Hugging Face secret or env var
    creds_dict = json.loads(gcp_creds_env)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = storage.Client(credentials=credentials, project=creds_dict.get("project_id"))
else:
    # Fall back to default method (e.g. GOOGLE_APPLICATION_CREDENTIALS as a file path or local login)
    client = storage.Client()

bucket = client.bucket(BUCKET_NAME)
def log_analytics(event_type: str, metadata: dict, content: str = None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "metadata": metadata
    }
    if content:
        entry["content"] = content

    # Create unique filename per event: analytics_logs/YYYY-MM-DD/HH-MM-SS_event.jsonl
    date_folder = datetime.now().strftime('%Y-%m-%d')
    time_stamp = datetime.now().strftime('%H-%M-%S-%f')[:-3]  # Include milliseconds
    log_filename = f"{LOG_DIR}/{date_folder}/{time_stamp}_{event_type}.jsonl"

    blob = bucket.blob(log_filename)
    blob.upload_from_string(json.dumps(entry) + "\n", content_type="application/jsonl")


def get_recent_generated_posts() -> list:
    posts = []
    blobs = list(client.list_blobs(BUCKET_NAME, prefix=LOG_DIR + "/"))
    blobs = sorted(blobs, key=lambda b: b.name, reverse=True)

    for blob in blobs:
        if not blob.name.endswith(".jsonl"):
            continue

        content = blob.download_as_text()
        lines = list(reversed(content.strip().splitlines()))
        for line in lines:
            try:
                data = json.loads(line)
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
