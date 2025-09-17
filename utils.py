import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
from werkzeug.security import check_password_hash

load_dotenv(override=True)

def add_to_google_sheet(jobs):
    # Load credentials from the JSON file
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SERVICE_ACCOUNT_FILE = "service_account.json"

    # Create a credentials object
    info = {
        "type": str(os.getenv('type')),
        "project_id": str(os.getenv('project_id')),
        "private_key_id": str(os.getenv('private_key_id')),
        "private_key": str(os.getenv('private_key')),
        "client_email": str(os.getenv('client_email')),
        "client_id": str(os.getenv('client_id')),
        "auth_uri": str(os.getenv('auth_uri')),
        "token_uri": str(os.getenv('token_uri')),
        "auth_provider_x509_cert_url": str(os.getenv('auth_provider_x509_cert_url')),
        "client_x509_cert_url": str(os.getenv('client_x509_cert_url')),
        "universe_domain": str(os.getenv('universe_domain')),
    }

    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Open the Google Sheet by its title or ID
    SPREADSHEET_ID = str(os.getenv('SPREADSHEET_ID'))
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Access the first sheet


    for job in jobs:
        # Append each job to the Google Sheet
        sheet.append_row([job['company'], job['role'], job['link']])



ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_HASH = os.getenv("ADMIN_HASH")

def authenticate(username, password):
    if username != ADMIN_USER:
        return False
    return check_password_hash(ADMIN_HASH, password)