import json
from datetime import datetime, timedelta, timezone
import requests

# Path to your JSON file
FILE_PATH = "downloads/listings.json"

SOFTWARE_CATEGORIES = ["Software", "Software Engineering"]

AIML_CATEGORIES = ["AI/ML/Data", "Data Science, AI & Machine Learning"]

def download_json():
    url = "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json"
    response = requests.get(url)
    data = response.json()
    
    # Save the JSON data to a file
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def extract_todays_openings(curr_id=0, category="software"):
    if category == "software":
        categories = SOFTWARE_CATEGORIES
    elif category == "aiml":
        categories = AIML_CATEGORIES
    # Load the JSON data
    with open(FILE_PATH, "r") as f:
        data = json.load(f)
    
    # Get date boundaries for the past 3 days (including today)
    now = datetime.now(timezone.utc)
    end_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc) + timedelta(days=1)
    start_of_period = end_of_day - timedelta(days=3)

    todays_openings = []
    for job in data:
        if "date_posted" not in job:
            continue
        
        posted_time = datetime.fromtimestamp(job["date_posted"], tz=timezone.utc)
        if start_of_period <= posted_time < end_of_day and job.get("category") in categories and job.get("active") == True and job.get("is_visible") == True and job.get("sponsorship") in ["Other", "Offers Sponsorship"]:
            # Calculate age in days
            days_ago = (now.date() - posted_time.date()).days
            age_str = f"{days_ago}d"
            
            # Format date_posted as "1-Nov, Sat"
            date_posted_str = f"{posted_time.day}-{posted_time.strftime('%b')}, {posted_time.strftime('%a')}"
            
            todays_openings.append({
                "company": job.get("company_name"),
                "role": job.get("title"),
                "location": ", ".join(job.get("locations", [])) if job.get("locations") else "N/A",
                "link": job.get("url"),
                "date_posted": date_posted_str,
                "age": age_str,
                "id": curr_id
            })
            curr_id += 1

    return todays_openings
