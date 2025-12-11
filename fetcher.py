# fetcher.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
BASE = "https://newsapi.org/v2"
MAX_RESULTS = 15

ALLOWED_COUNTRIES = {"au","ca","jp","ae","sa","kr","us","ma"}
ALLOWED_LANGUAGES = {"ar","en"}
ALLOWED_CATEGORIES = {"business","general","health","science","sports","technology"}

def _call_api(endpoint, params):
    params = {k:v for k,v in params.items() if v}
    params["apiKey"] = API_KEY
    resp = requests.get(f"{BASE}/{endpoint}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_headlines(q=None, category=None, country=None):
    if country and country not in ALLOWED_COUNTRIES:
        raise ValueError("Invalid country code.")
    if category and category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category.")
    params = {"q": q, "category": category, "country": country, "pageSize": MAX_RESULTS}
    return _call_api("top-headlines", params)

def get_sources(category=None, country=None, language=None):
    if category and category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category.")
    if country and country not in ALLOWED_COUNTRIES:
        raise ValueError("Invalid country.")
    if language and language not in ALLOWED_LANGUAGES:
        raise ValueError("Invalid language.")
    params = {"category": category, "country": country, "language": language}
    return _call_api("sources", params)

