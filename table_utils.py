import json
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from flask import render_template
import requests

github_url = 'https://github.com/SimplifyJobs/New-Grad-Positions'

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

def extract_todays_openings_from_readme(category="software"):
    # OLD CODE FOR SCRAPING THE README FILE
    # Scrape https://github.com/SimplifyJobs/New-Grad-Positions README file and display contents
    # Use requests and BeautifulSoup to scrape the README file

    # OLD
    response = requests.get(github_url)

    # Parse the README file using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the table in the README file
    readme = soup.find('article', class_='markdown-body entry-content container-lg')

    # NEW
    # response = requests.get(github_url)

    # soup = BeautifulSoup(response.content, 'html.parser')
    # # Extract from <react-partial data-attempted-ssr="true" data-ssr="false" partial-name="repos-overview">
    # data = soup.find('react-partial', {'data-ssr': 'false', 'data-attempted-ssr': 'true', 'partial-name': 'repos-overview'})
    # # Extract <script data-target="react-partial.embeddedData" type="application/json"> from data
    # data = data.find('script', {'data-target': 'react-partial.embeddedData', 'type': 'application/json'})
    # json_data = json.loads(data.contents[0])

    # readme = json_data['props']['initialPayload']['overview']['overviewFiles'][0]['richText']
    # # Convert string to BeautifulSoup object
    # readme = BeautifulSoup(readme, 'html.parser')

    if not readme:
        return render_template('error.html', message='README not found')
    table = readme.find('table')

    # Not needed in new version
    # today = datetime.now().strftime('%b %d')
    rows = table.find_all('tr')

    first_row = rows[0]

    rows.remove(first_row)
    # Filter rows by last three days (0d, 1d, 2d)
    rows = [row for row in rows if row.find_all('td')[4].text.strip() == "0d" or row.find_all('td')[4].text.strip() == "1d" or row.find_all('td')[4].text.strip() == "2d"]
    # Filter by open applications
    rows = [row for row in rows if row.find_all('td')[3].text.strip() != '🔒']

    headers = ['company', 'role', 'location', 'link', 'age']

    todays_jobs = []
    for id, row in enumerate(rows):
        job = {}
        job['id'] = id
        for i, td in enumerate(row.find_all('td')):
            if i == 0:
                if td.text.strip() == '↳':
                    job[headers[i]] = todays_jobs[-1]['company']
                else:
                    if td.find('strong'):
                        job[headers[i]] = td.find('strong').find('a').text.strip()
                    else:
                        job[headers[i]] = td.text.strip()
            elif i == 1:
                job[headers[i]] = td.text.strip()
            elif i == 2:
                if td.find('br'):
                    job[headers[i]] = td.get_text(separator=' & ').strip()
                else:
                    job[headers[i]] = td.text.strip()
            elif i == 3:
                job[headers[i]] = td.find('a')['href']
            elif i == 4:
                job[headers[i]] = td.text.strip()
        todays_jobs.append(job)

    return todays_jobs