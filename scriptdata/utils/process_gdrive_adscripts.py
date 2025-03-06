import os
import re
import io
import sys
import time
import shutil
import django
import random
import logging
import zipfile
import webcolors
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files import File
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.db import connection, transaction
from googleapiclient.http import MediaIoBaseDownload


# Setup
def setup_django():
    """Ensures Django settings are configured before using ORM or settings."""
    project_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_path)
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
        django.setup()

setup_django()
from scriptdata.models import AdScript
from scriptdata.utils.embeddings import generate_embedding, index


# Logging
LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, 'process_gdrive_adscripts_log.log')
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.stream.reconfigure(encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, stream_handler],
)
logger = logging.getLogger(__name__)


# Config
SERVICE_ACCOUNT_FILE = "galvanized-app-445607-e7-1604e087ad17.json"
GDRIVE_FOLDER_ID = settings.GDRIVE_FOLDER_ID
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents.readonly"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build("drive", "v3", credentials=creds)
docs_service = build("docs", "v1", credentials=creds)
INTEGRATIONS = ('FACEBOOK', 'FB', 'YT', 'YOUTUBE', 'GOOGLE', 'SNAPCHAT', 'TIKTOK', 'TWITTER', 'LINKEDIN')
TEMP_FOLDER = os.path.join(settings.BASE_DIR, "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)



class ExtractAd:
    def __init__(self):
        pass


    # GET HTML FILES FROM GOOGLE DRIVE
    def list_google_docs(self, folder_id):
        """Function to get all Google Docs from the specified folder using pagination."""
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
        all_files = []
        page_token = None
        while True:
            results = drive_service.files().list(
                q=query,
                fields="nextPageToken, files(id, name)",
                pageSize=1000,  # Max allowed: 1000
                pageToken=page_token
            ).execute()
            files = results.get('files', [])
            all_files.extend(files)
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        return all_files


    def fetch_gdrive_docs(self, file_id, file_name):
        """Function to download and save Google Docs as HTML Web Page"""
        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType='application/zip'  # Export as ZIP (contains HTML + assets)
        )
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        file_stream.seek(0)

        # Extract ZIP contents
        with zipfile.ZipFile(file_stream, 'r') as zip_ref:
            html_files = [f for f in zip_ref.namelist() if f.endswith('.html')]  # Find HTML file
            if not html_files:
                logger.warning(f"No HTML file found in the exported ZIP for {file_name}")
                return

            html_filename = html_files[0]
            extracted_html = zip_ref.read(html_filename)

        # Clean filename
        output_filename = re.sub(r'[\/:*?"<>|]', '_', f"{file_name}")
        output_filename = f"{output_filename}__-__{file_id}.html"
        file_path = os.path.join(TEMP_FOLDER, output_filename)
        with open(file_path, "wb") as f:
            f.write(extracted_html)
        logger.info(f"Processed: {file_name} ({file_id}) --> {output_filename}")


    # HIGHLIGHT DETECTION
    def get_rgb(self, color):
        try:
            if color.startswith("#"):
                return webcolors.hex_to_rgb(color)
            else:
                return webcolors.name_to_rgb(color)
        except ValueError:
            return None


    def is_gray(self, rgb):
        if rgb:
            r, g, b = rgb.red, rgb.green, rgb.blue
            return abs(r - 153) <= 60 and abs(g - 153) <= 60 and abs(b - 153) <= 60


    def is_red(self, rgb):
        if rgb:
            r, g, b = rgb.red, rgb.green, rgb.blue
            return r >= 200 and g <= 25 and b <= 25


    def extract_from_html(self, file_path):
        if file_path.endswith(".html"):
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

            all_colors = {}
            style_tag = soup.find("style")

            if style_tag:
                css_text = style_tag.get_text()
                class_patterns = re.findall(r"(\.c\d+)\s*\{([^}]*)\}", css_text)

                for class_name, styles in class_patterns:
                    colors_found = []
                    color_matches = re.findall(r"(color|background-color)\s*:\s*([^;]+);?", styles)

                    for _, color_value in color_matches:
                        rgb = self.get_rgb(color_value.strip())
                        if rgb:
                            colors_found.append(color_value.strip())

                    if colors_found:
                        all_colors[class_name[1:]] = colors_found

            # Classes to exclude (gray or red)
            excluded_classes = {
                cls for cls, colors in all_colors.items()
                if any(self.is_gray(self.get_rgb(c)) or self.is_red(self.get_rgb(c)) for c in colors)
            }

            for elem in soup.find_all(class_=True):
                elem_classes = list(set(elem.get("class", [])))
                if any(cls in excluded_classes for cls in elem_classes):
                    elem.decompose()  

            # Remove text inside anchor tags
            for a_tag in soup.find_all("a"):
                a_tag.string = ""

            # Remove excessive newlines and spaces
            cleaned_text = soup.get_text("\n", strip=True)
            cleaned_text = re.sub(r"\n{2,}", "\n\n", cleaned_text)
            cleaned_text = re.sub(r" {4,}", " ", cleaned_text)

            # **Instruction Removal Logic**
            lines = cleaned_text.split("\n")
            script_index = next(
                (i for i, line in enumerate(lines) if re.match(r"^\s*(script|scripts)\s*:?\s*$", line, re.IGNORECASE)),
                None
            )

            if script_index is not None:
                lines = lines[script_index + 1:]
            cleaned_text = "\n".join(lines)
            return cleaned_text
        else:
            return ''
        

    # FILE METADATA
    def extract_metadata_from_filename(self, filename):
        """
        Extract metadata from the filename.
        """
        metadata = {
            "platform": None,
            "ad_type": None,
            "industry": None,
        }
        for name in INTEGRATIONS:
            if name.lower() in filename.lower():
                metadata["platform"] = name

        # Extract ad type from keywords
        if "UGC" in filename:
            metadata["ad_type"] = "User-Generated Content"
        elif "Expert" in filename:
            metadata["ad_type"] = "Expert Interview"
        elif "Testimonial" in filename:
            metadata["ad_type"] = "Testimonial"
        return metadata
        

    def extract_metadata_from_content(self, text):
        """
        Extract industry and additional metadata from the script content.
        """
        metadata = {
            "industry": None
        }

        # Common industry keywords
        industry_keywords = {
            "skincare": ["skin", "moisturizer", "wrinkles", "collagen"],
            "fitness": ["workout", "exercise", "protein", "gym"],
            "finance": ["investment", "money", "trading", "credit score"],
            "tech": ["AI", "software", "machine learning"]
        }

        for industry, keywords in industry_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                metadata["industry"] = industry
                break
        return metadata
        

    # ADD DATA TO DATABASE
    @transaction.atomic
    def process_docx(self, file_path):
        """
        Processes HTML file, extracts metadata, and saves to the database.
        """
        filename = os.path.basename(p=file_path)
        filename, file_id = filename.rsplit("__-__", 1)
        file_id = file_id.rsplit(".", 1)[0]
        filename = filename[:253]
        text_content = self.extract_from_html(file_path=file_path)
        metadata_from_filename = self.extract_metadata_from_filename(filename=filename)
        metadata_from_content = self.extract_metadata_from_content(text=text_content)

        # Combine metadata sources
        platform = metadata_from_filename.get("platform", "") or ""
        ad_type = metadata_from_filename.get("ad_type", "") or ""
        industry = metadata_from_content.get("industry", "") or metadata_from_filename.get("industry", "") or ""
        with open(file_path, 'rb') as f:
            django_file = File(f)
            ad_script = AdScript.objects.get_or_create(
                filename=filename,
                file_id=file_id,
                defaults={
                    "platform": platform,
                    "ad_type": ad_type,
                    "industry": industry,
                    "content": text_content
                }
            )
            ad_script[0].ad_file.save(f"{filename[:50]}_{file_id}.html", django_file, save=True)

        # Generate embedding & save to pinecone
        embedding_vector = generate_embedding(text_content)
        index.upsert([(filename, embedding_vector, {"file_id": file_id, "platform": platform, 
                                                    "ad_type": ad_type, "industry": industry})])
        logger.info(f"Saved: {filename} → Pinecone (Platform: {platform}, Ad Type: {ad_type}, Industry: {industry})")


    def batch_process_docs(self, temp_folder):
        """
        Processes all .docx files in the given folder and saves them to the database.
        """
        logger.info("Initiating batch processing of ad script docx...")
        for filename in os.listdir(temp_folder):
            wait_time = random.randint(5, 10)
            logger.info(f"Processing Doc: {filename}")
            if filename.endswith(".html"):
                file_path = os.path.join(temp_folder, filename)
                self.process_docx(file_path)
            time.sleep(wait_time)


    def chunk_list(self, docs, batch_size):
        """Yield successive chunks from list."""
        for i in range(0, len(docs), batch_size):
            yield docs[i:i + batch_size]


    def process_google_ad_scripts(self, limit=None, batch_size=10):
        docs = self.list_google_docs(folder_id=GDRIVE_FOLDER_ID)
        if not docs:
            logger.info("No Google Docs found in the specified folder.")
            return
        if limit:
            docs = docs[:limit]

        for batch_number, batch in enumerate(self.chunk_list(docs, batch_size), start=1):
            logger.info(f"** Processing batch {batch_number} ({len(batch)} docs) out of total {len(docs)} docs **")
            for doc in batch:
                self.fetch_gdrive_docs(doc['id'], doc['name'])
            logger.info("Initiating batch processing of downloaded docs...")
            self.batch_process_docs(temp_folder=TEMP_FOLDER)
            if os.path.exists(TEMP_FOLDER):
                shutil.rmtree(TEMP_FOLDER)
            os.makedirs(TEMP_FOLDER, exist_ok=True)
        logger.info("Processing Complete!")


if __name__ == '__main__':
    try:
        ad_extracter = ExtractAd()
        ad_extracter.process_google_ad_scripts()
        logger.info("Processing Complete!")
    except Exception as e:
        logger.error(f"Error while processing google ad scripts: ", exc_info=True)
    finally:
        connection.close()


