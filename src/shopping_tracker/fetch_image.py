import requests

def fetch_image(image_url: str) -> bytes:
    response = requests.get(image_url)
    response.raise_for_status()
    return response.content