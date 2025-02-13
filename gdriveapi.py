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

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents.readonly"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build("drive", "v3", credentials=creds)
docs_service = build("docs", "v1", credentials=creds)

# Fetch Google Docs files from the Drive
def list_google_docs_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
    results = drive_service.files().list(q=query, fields="files(id, name, createdTime, size)").execute()
    return results.get("files", [])

# Extract text from Google Docs
def get_document_text(doc_id):
    document = docs_service.documents().get(documentId=doc_id).execute()
    text = "".join(
        content["paragraph"]["elements"][0].get("textRun", {}).get("content", "")
        for content in document.get("body", {}).get("content", [])
        if "paragraph" in content
    )
    return text

# Process Files
docs = list_google_docs_in_folder(GDRIVE_FOLDER_ID)
if docs:
    for doc in docs:
        print(f"Processing: {doc['name']} ({doc['id']})")
        
        # Extract metadata
        name = doc['name']
        created_on = doc['createdTime']
        size = doc.get('size', 'Unknown')
        
        # Extract content
        text_content = get_document_text(doc['id'])
        
        # Save to text file
        output_filename = f"{name}.txt"
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(f"Name - {name}\n")
            file.write(f"Size - {size}\n")
            file.write(f"Created on - {created_on}\n")
            file.write(f"Content -\n{text_content}")
        
        print(f"Saved: {output_filename}")
else:
    print("No Google Docs files found in the folder.")

