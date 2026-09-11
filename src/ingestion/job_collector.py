import os
import json
import requests

from pathlib import Path
from dotenv import load_dotenv


# Load API credentials from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")


# Adzuna country code
COUNTRY = "in"

# Search page
PAGE = 1

# What jobs we want
KEYWORD = "data engineer"

# Where we want to search
LOCATION = "India"


url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{PAGE}"

params = {
    "app_id": APP_ID,
    "app_key": API_KEY,
    "what": KEYWORD,
    "where": LOCATION,
    "results_per_page": 50
}


response = requests.get(url, params=params, timeout=30)

print("Status code:", response.status_code)

response.raise_for_status()

data = response.json()


# Create raw data directory
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)


# Save the complete API response
output_file = output_dir / "jobs.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)


print("Jobs collected:", len(data.get("results", [])))
print("Raw data saved to:", output_file)