from flask import Flask, render_template, request, redirect
import utils
import table_utils
app = Flask(__name__)

github_url = 'https://github.com/SimplifyJobs/New-Grad-Positions'


@app.route('/', methods=['GET'])
def main():
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