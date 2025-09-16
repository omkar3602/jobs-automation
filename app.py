from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import utils
import table_utils
app = Flask(__name__)

github_url = 'https://github.com/SimplifyJobs/New-Grad-Positions'




@app.route('/', methods=['GET'])
def main():
    '''
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
    # Filter rows by today's date
    rows = [row for row in rows if row.find_all('td')[4].text.strip() == "0d"]
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
    '''

    # NEW CODE FOR READING FROM JSON FILE
    table_utils.download_json()

    todays_jobs = table_utils.extract_todays_openings(category="software")

    return render_template('index.html', todays_jobs=todays_jobs)

@app.route('/aiml/', methods=['GET'])
def aiml_jobs():
    table_utils.download_json()

    todays_jobs = table_utils.extract_todays_openings(category="aiml")
    return render_template('index.html', todays_jobs=todays_jobs)

@app.route('/', methods=['POST'])
def main_post():
    if request.method == 'POST':
        # print(request.form.getlist('selected_job_ids'))
        # print(request.form.getlist('todays_jobs'))
        selected_job_ids = request.form.getlist('selected_job_ids')
        selected_job_ids = [int(id) for id in selected_job_ids]
        todays_jobs = request.form.getlist('todays_jobs')
        todays_jobs = eval(todays_jobs[0])
        selected_jobs = [todays_jobs[id] for id in selected_job_ids]

        # Add selected jobs to google sheet
        utils.add_to_google_sheet(selected_jobs)
        return redirect('/success/')

@app.route('/success/', methods=['GET'])
def added():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(host='localhost', port=8000)