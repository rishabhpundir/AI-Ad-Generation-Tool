import os
import django
import pandas as pd
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()

# Google Drive API Config
SERVICE_ACCOUNT_FILE = "galvanized-app-445607-e7-1604e087ad17.json"
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")

SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# Fetch Files from the Drive
def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

# Read File into Pandas
def download_file(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_stream = BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_stream.seek(0)
    return file_stream

# Process Files
files = list_files_in_folder(GDRIVE_FOLDER_ID)
if files:
    for file in files:
        print(f"Processing: {file['name']} ({file['id']})")
        excel_data = download_file(file["id"])
        df = pd.read_excel(excel_data, engine="openpyxl")
        csv_filename = file["name"].replace(".xlsx", ".csv")
        df.to_csv(csv_filename, index=False)
        print(f"Saved: {csv_filename}")
else:
    print("No Excel files found in the folder.")

