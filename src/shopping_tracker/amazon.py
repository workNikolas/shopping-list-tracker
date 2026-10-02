from bs4 import BeautifulSoup
from decimal import Decimal
from urllib.parse import urlparse

import requests

class AmazonFetcher:
    def __init__(self, url: str):
        self.url = url

    def fetch(self, ) -> str:
        headers = {
            "headers": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
                )
        }
        response = requests.get(
            self.url,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        return response.text
  

class AmazonParser:
    def __init__(self, html:str):
        self.soup = BeautifulSoup(html, "html.parser")

    def to_dict(self):
        return {
            "title": self.parse_title(),
            "trice": self.parse_price(),
            "avg_Rating": self.parse_rating(),
            "availability": self.parse_availability(),
        }

    def parse_title(self) -> str | None:
        title_element = self.soup.find(id="productTitle")
        if title_element is None:
            print("No title element found")
            return None

        return title_element.get_text(strip=True)


    def parse_price(self) -> Decimal | None:
        symbol_element = self.soup.find(class_="a-price-symbol")
        whole_element = self.soup.find(class_="a-price-whole")
        fraction_element = self.soup.find(class_="a-price-fraction")

        if any(element is None for element in (symbol_element, whole_element, fraction_element)):
            print("No price found")
            return None

        symbol = symbol_element.get_text(strip=True)
        whole = whole_element.get_text(strip=True)
        whole = whole.replace(",", "")
        fraction = fraction_element.get_text(strip=True)

        price = Decimal(f"{whole}.{fraction}")
        return price

    def parse_rating(self) -> float | None:
        rating_element = self.soup.find(id="acrPopover")
        if rating_element is None: 
            return None
        
        rating = rating_element.get("title").split(" ")[0]
        rating = float(rating.replace(",", "."))
        return rating

    def parse_availability(self) -> str | None:
        availability_element = self.soup.find(id="availability")

        if availability_element is None:
            return None

        return availability_element.get_text(strip=True)

    def parse_cover(self) -> str | None:
        image_element = self.soup.find(id="landingImage")

        if image_element is None:
            return None

        image_url = image_element.get("data-old-hires")

        if image_url is not None:
            return image_url

        image_url = image_element.get("src")

        if image_url is not None:
            return image_url

        return None
        
def get_asin(url: str) -> str | None:
    parsed_url = urlparse(url)
    parts = parsed_url.path.split("/")

    try:
        dp_index = parts.index("dp")
        candidate = parts[dp_index + 1]
    except (ValueError, IndexError):
        return None

    if len(candidate) != 10 or not candidate.isalnum():
        return None
    
    return candidate