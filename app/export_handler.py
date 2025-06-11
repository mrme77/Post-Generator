import os
from datetime import datetime

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_to_txt(text: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(EXPORT_DIR, f"socialmedia_post_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    
    return filename
