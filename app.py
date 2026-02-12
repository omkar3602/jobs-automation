from flask import Flask, render_template, request, redirect, session
import utils
import table_utils
from decorators import login_required
from dotenv import load_dotenv
import os

load_dotenv(override=True)


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_fallback_key")

github_url = 'https://github.com/SimplifyJobs/New-Grad-Positions'


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if utils.authenticate(username, password):
            session["user"] = username
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route('/', methods=['GET'])
def main():
    is_logged_in = 'user' in session

    # NEW CODE FOR READING FROM JSON FILE
    table_utils.download_json()

    todays_jobs = table_utils.extract_todays_openings(category="software")

    return render_template('index.html', todays_jobs=todays_jobs, category="software", is_logged_in=is_logged_in)

@app.route('/aiml/', methods=['GET'])
def aiml_jobs():
    is_logged_in = 'user' in session

    table_utils.download_json()

    todays_jobs = table_utils.extract_todays_openings(category="aiml")
    return render_template('index.html', todays_jobs=todays_jobs, category="aiml", is_logged_in=is_logged_in)

@app.route('/', methods=['POST'])
@login_required
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
@login_required
def added():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(host='localhost', port=8002)