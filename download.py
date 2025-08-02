import os
import requests

def download_image(image_url, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
    except Exception:
        pass
    return None
