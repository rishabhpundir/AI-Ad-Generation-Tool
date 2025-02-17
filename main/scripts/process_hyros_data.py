import os
import sys
import glob
import json
import django
import logging
from django.conf import settings
from django.db import connection, transaction

def setup_django():
    """Ensures Django settings are configured before using ORM or settings."""
    project_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_path)
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
        django.setup()

# Setup
setup_django()
from django.db import connection, transaction
from main.models import TrafficSource, AdSource, Source, Ad, Lead, Tag


# Logging configuration
LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file_path = os.path.join(LOG_DIR, 'process_hyros_data_log.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler(sys.stdout)    # Log to console
    ]
)
logger = logging.getLogger(__name__)



class AddJSONDataToModels:
    help = "Import data from Hyros JSON files into Django models"

    def __init__(self):
        self.INTEGRATIONS = ['FACEBOOK', 'GOOGLE', 'SNAPCHAT', 'TIKTOK', 'TWITTER', 'LINKEDIN']
        self.BASE_DIR = os.path.join(settings.BASE_DIR.parent, 'output')

    def get_json_files(self, source):
        json_files = []
        if source not in ['leads', 'tags']:
            for integration in self.INTEGRATIONS:
                source_path = os.path.join(self.BASE_DIR, source)
                integration_path = os.path.join(source_path, integration)
        else:
                source_path = os.path.join(self.BASE_DIR, source)
                integration_path = source_path
        if os.path.isdir(integration_path):
            json_files.extend(glob.glob(os.path.join(integration_path, "*.json")))
        return json_files

    @transaction.atomic
    def import_traffic_sources(self, json_files_path):
        """Extract and insert Traffic Sources"""
        for source_file in json_files_path:
            with open(source_file, "r") as file:
                data = json.load(file)
            
            for entry in data["result"]:
                traffic_source_id = entry["trafficSource"]["id"]
                traffic_source_name = entry["trafficSource"]["name"]

                traffic_source, created = TrafficSource.objects.get_or_create(
                    external_id=traffic_source_id,
                    defaults={"name": traffic_source_name}
                )

                # if created:
                #     print(f"Added Traffic Source: {traffic_source_name}")

    @transaction.atomic
    def import_ad_sources(self, json_files_path):
        """Extract and insert Ad Sources from Sources JSON"""
        for source_file in json_files_path:
            with open(source_file, "r") as file:
                data = json.load(file)

            for entry in data["result"]:
                ad_source_data = entry["adSource"]
                ad_source_id = ad_source_data["adSourceId"]
                ad_account_id = ad_source_data["adAccountId"]
                platform = ad_source_data["platform"]

                ad_source, created = AdSource.objects.get_or_create(
                    ad_source_id=ad_source_id,
                    defaults={"ad_account_id": ad_account_id, "platform": platform}
                )

                # if created:
                #     print(f"Added Ad Source: {platform} - {ad_source_id}")

    @transaction.atomic
    def import_sources(self, json_files_path):
        """Extract and insert Sources"""
        for source_file in json_files_path:
            with open(source_file, "r") as file:
                data = json.load(file)

            for entry in data["result"]:
                ad_source = AdSource.objects.filter(ad_source_id=entry["adSource"]["adSourceId"]).first()
                traffic_source = TrafficSource.objects.filter(external_id=entry["trafficSource"]["id"]).first()

                source, created = Source.objects.get_or_create(
                    tag=entry["tag"],
                    defaults={
                        "name": entry["name"],
                        "disregarded": entry["disregarded"],
                        "organic": entry["organic"],
                        "ad_source": ad_source,
                        "traffic_source": traffic_source,
                        "creation_date": str(entry["creationDate"])
                    }
                )

                # if created:
                #     print(f"Added Source: {source.name}")

    @transaction.atomic
    def import_ads(self, json_files_path):
        """Extract and insert Ads"""
        for ad_file in json_files_path:
            with open(ad_file, "r") as file:
                data = json.load(file)

            for entry in data["result"]:
                source = Source.objects.filter(tag=entry["source"]["tag"]).first()
                if source is not None:
                    ad, created = Ad.objects.get_or_create(
                        name=entry["name"],
                        defaults={
                            "source": source,
                            "creation_date": str(entry["creationDate"])
                        }
                    )

                    # if created:
                    #     print(f"Added Ad: {ad.name}")

    @transaction.atomic
    def import_leads(self, json_files_path):
        """Extract and insert Leads"""
        for lead_file in json_files_path:
            with open(lead_file, "r") as file:
                data = json.load(file)

            for entry in data["result"]:
                if "firstSource" in entry and "lastSource" in entry:
                    first_source = Source.objects.filter(tag=entry["firstSource"]["tag"]).first()
                    last_source = Source.objects.filter(tag=entry["lastSource"]["tag"]).first()

                    lead, created = Lead.objects.get_or_create(
                        external_id=entry["id"],
                        defaults={
                            "email": entry["email"],
                            "creation_date": str(entry["creationDate"]),
                            "first_name": entry.get("firstName", ""),
                            "last_name": entry.get("lastName", ""),
                            "ips": entry.get("ips", []),
                            "phone_numbers": entry.get("phoneNumbers", []),
                            "tags": entry.get("tags", []),
                            "first_source": first_source,
                            "last_source": last_source,
                        }
                    )

                    # if created:
                    #     print(f"Added Lead: {lead.email}")

    @transaction.atomic
    def import_tags(self, json_files_path):
        """Extract and insert tags"""
        for tag_file in json_files_path:
            with open(tag_file, "r") as file:
                data = json.load(file)

            for entry in data["result"]:
                tag, created = Tag.objects.get_or_create(tag=entry)



if __name__ == "__main__":
    try:
        json2db = AddJSONDataToModels()
        output_list = ['sources', 'ads', 'leads', 'tags']
        for output in output_list:
            json_files_path = json2db.get_json_files(source=output)
            if output == "sources":
                json2db.import_traffic_sources(json_files_path=json_files_path)
                logger.info("Read & saved traffic JSONe done!!")
                json2db.import_ad_sources(json_files_path=json_files_path)
                logger.info("Read & saved ad JSONe done!!")
                json2db.import_sources(json_files_path=json_files_path)
                logger.info("Read & saved source JSON!")
            elif output == "ads":
                json2db.import_ads(json_files_path=json_files_path)
                logger.info("Read & saved ads JSON!")
            elif output == "leads":
                json2db.import_leads(json_files_path=json_files_path)
                logger.info("Read & saved leads JSON!")
            elif output == "tags":
                json2db.import_tags(json_files_path=json_files_path)
                logger.info("Read & saved tags JSON!")

        logger.info("DONE!!!!!")
    except Exception as e:
        logger.info(f"Error while reading Hyros JSON data: {e}", exc_info=True)
    finally:
        connection.close()


