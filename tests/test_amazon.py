from src.shopping_tracker.amazon import get_asin


def test_extract_asin_from_simple_url():
    url = "https://amazon.com.br/dp/0486223051"

    assert get_asin(url) == "0486223051"


def test_extract_alphanumeric_asin():
    url = "https://amazon.com.br/dp/B0DHDZH8B9"

    assert get_asin(url) == "B0DHDZH8B9"


def test_extract_asin_from_url_with_ref():
    url = "https://amazon.com.br/book/dp/B0DHDZH8B9/ref=abc"

    assert get_asin(url) == "B0DHDZH8B9"


def test_extract_asin_from_url_with_query():
    url = "https://amazon.com.br/dp/B0DHDZH8B9?tag=abc"

    assert get_asin(url) == "B0DHDZH8B9"


def test_extract_asin_returns_none_without_dp():
    url = "https://amazon.com.br/not-a-product"

    assert get_asin(url) is None


def test_extract_asin_returns_none_for_invalid_asin():
    url = "https://amazon.com.br/dp/123asd/l3/not-a-product"

    assert get_asin(url) is None