import os
import sys
import json
import django
import logging
import requests
import traceback
from django.conf import settings
from django.utils import timezone
from django.db import connection, transaction


# Setup
def setup_django():
    """Ensures Django settings are configured before using ORM or settings."""
    project_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_path)
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
        django.setup()

setup_django()
from main.models import AdSource, AdAccountAtrribution


# Logging configuration
LOG_DIR = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

log_file_path = os.path.join(LOG_DIR, 'get_hyros_data_log.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler(sys.stdout)    # Log to console
    ]
)
logger = logging.getLogger(__name__)


# Configuration
HYROS_API_KEY = settings.HYROS_API_KEY
HEADERS = {'API-Key': HYROS_API_KEY}
INTEGRATIONS = ['FACEBOOK', 'GOOGLE', 'SNAPCHAT', 'TIKTOK', 'TWITTER', 'LINKEDIN']
OUTPUT_PATH = os.path.join(settings.BASE_DIR, 'output')
os.makedirs(OUTPUT_PATH, exist_ok=True)  # Ensure output directory exists


class FetchHyrosData:
    """Class to handle fetching data from Hyros API and saving it."""
    def __init__(self):
        pass

    # Fetch data Hyros API
    def fetch_hyros_data(self, url, params=None):
        response = requests.get(url=url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error {response.status_code}: {response.text}", exc_info=True)
            return None

    # Save data as a JSON file
    def save_as_json(self, data, folder_name, filename):
        destination_folder = os.path.join(OUTPUT_PATH, folder_name)
        os.makedirs(destination_folder, exist_ok=True)
        file_path = os.path.join(destination_folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_dates(self):
        now = timezone.localtime(timezone.now())
        # end date
        end_date = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_date = end_date[:-2] + ":" + end_date[-2:]
        # start date
        start_date_dt = now.replace(year=2001, month=1, day=1, hour=0, minute=0, second=0)
        start_date = start_date_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_date = start_date[:-2] + ":" + start_date[-2:]
        return start_date, end_date

    def get_sources(self):
        for integration in INTEGRATIONS:
            num = 1
            pageId = ""
            next_page = True
            while next_page:
                url_sources = f'https://api.hyros.com/v1/api/v1.0/sources?integrationType={integration}&pageSize=250&pageId={pageId}'
                url = url_sources
                filename = f"sources_{integration}_{num}"

                data = self.fetch_hyros_data(url=url)
                pageId = data.get('nextPageId', None)
                if data:
                    logger.info("Sources API request sent")
                    self.save_as_json(data=data, filename=f"{filename}.json")
                    logger.info("Sources Data saved as JSON successfully!")
                else:
                    logger.error("Failed to Sources fetch data: ", exc_info=True)

                if pageId is None:
                    next_page = False
                num += 1


    def get_ads(self):
        for integration in INTEGRATIONS:
            num = 1
            pageId = ""
            next_page = True
            while next_page:
                url_ads = f'https://api.hyros.com/v1/api/v1.0/ads?integrationTpe={integration}&pageSize=250&pageId={pageId}'
                url = url_ads
                filename = f"ads_{integration}_{num}"

                data = self.fetch_hyros_data(url=url)
                pageId = data.get('nextPageId', None)
                if data:
                    logger.info("Ads API request sent")
                    self.save_as_json(data=data, filename=f"{filename}.json")
                    logger.info("Ads Data saved as JSON successfully!")
                else:
                    logger.error("Failed to fetch Ads data: ", exc_info=True)

                if pageId is None:
                    next_page = False
                num += 1

    def get_leads(self):
        num = 1
        pageId = ""
        next_page = True
        while next_page:
            url_leads = f'https://api.hyros.com/v1/api/v1.0/leads?fromDate=2025-01-01T00:00:00-05:00&toDate=2025-02-06T00:00:00-05:00&pageSize=250&pageId={pageId}'
            filename = f"leads_{num}"

            data = self.fetch_hyros_data(url=url_leads)
            pageId = data.get('nextPageId', None)
            if data:
                logger.info("Leads API request sent")
                self.save_as_json(data=data, filename=f"{filename}.json")
                logger.info("Leads Data saved as JSON successfully!")
            else:
                logger.error("Failed to fetch Leads data: ", exc_info=True)

            if pageId is None:
                next_page = False
            num += 1

    def get_tags(self):
        num = 1
        pageId = ""
        next_page = True
        while next_page:
            url_leads = f'https://api.hyros.com/v1/api/v1.0/tags'
            filename = f"tags_{num}"

            data = self.fetch_hyros_data(url=url_leads)
            pageId = data.get('nextPageId', None)
            if data:
                logger.info("Tags API request sent")
                self.save_as_json(data=data, folder_name="tags", 
                                  filename=f"{filename}.json")
                logger.info("Tags Data saved as JSON successfully!")
            else:
                logger.error("Failed to fetch Tags data: ", exc_info=True)

            if pageId is None:
                next_page = False
            num += 1

    # @transaction.atomic
    def get_ad_account_attribution(self, attribution_model, start_date, end_date):
        fields = "cost,impressions,clicks,ctr,cost_per_click,leads,cost_per_lead,sales,cost_per_sale,unique_sales,cost_per_unique_sale,aov,roas,total_revenue,profit"
        currency = "user_currency"
        ad_sources = AdSource.objects.all()
        for ad_source in ad_sources:
            platform = ad_source.platform.lower()
            ad_account_id = ad_source.ad_account_id
            url_leads = f'https://api.hyros.com/v1/api/v1.0/attribution/ad-account?attributionModel={attribution_model}' \
                        f'&startDate={start_date}&endDate={end_date}&fields={fields}&ids={ad_account_id}&currency={currency}'
            filename = f"attrib_ad_account_{platform}_{ad_account_id}"

            data = self.fetch_hyros_data(url=url_leads)
            if data:
                self.save_as_json(data=data, 
                                  folder_name="attribution",
                                  filename=f"{filename}.json")

                attr_id = data.get("result")[0]["id"]
                clicks = data.get("result")[0]["clicks"]
                cost = data.get("result")[0]["cost"]
                cost_per_click = data.get("result")[0]["cost_per_click"]
                cost_per_lead = data.get("result")[0]["cost_per_lead"]
                cost_per_sale = data.get("result")[0]["cost_per_sale"]
                cost_per_unique_sales = data.get("result")[0]["cost_per_unique_sales"]
                average_order_value = data.get("result")[0]["average_order_value"]
                ctr = data.get("result")[0]["ctr"]
                impressions = data.get("result")[0]["impressions"]
                leads = data.get("result")[0]["leads"]
                profit = data.get("result")[0]["profit"]
                roas = data.get("result")[0]["roas"]
                sales = data.get("result")[0]["sales"]
                total_revenue = data.get("result")[0]["total_revenue"]
                unique_sales = data.get("result")[0]["unique_sales"]
                end_date = data.get("result")[0]["end_date"]
                start_date = data.get("result")[0]["start_date"]
                with transaction.atomic():
                    adattr, created = AdAccountAtrribution.objects.get_or_create(
                        ad_source=ad_source,
                        defaults={
                            "attr_id": attr_id,
                            "attribution_model": attribution_model,
                            "clicks": clicks,
                            "cost": cost,
                            "cost_per_click": cost_per_click,
                            "cost_per_lead": cost_per_lead,
                            "cost_per_sale": cost_per_sale,
                            "cost_per_unique_sales": cost_per_unique_sales,
                            "average_order_value": average_order_value,
                            "ctr": ctr,
                            "impressions": impressions,
                            "leads": leads,
                            "profit": profit,
                            "roas": roas,
                            "sales": sales,
                            "total_revenue": total_revenue,
                            "unique_sales": unique_sales,
                            "end_date": end_date,
                            "start_date": start_date
                        }
                    )
                    logger.info(f"Ad Attribution data saved -> {adattr}")
            else:
                logger.error("Failed to fetch Ad Attribution data: ", exc_info=True)


# Script execution block
if __name__ == "__main__":
    try:
        hyros = FetchHyrosData()
        attribution_model = "first_click"
        start_date, end_date = hyros.get_dates()
        hyros.get_ad_account_attribution(attribution_model, start_date, end_date)
        hyros.get_tags()
    except Exception as e:
        logger.error(f"Error while accessing Hyros API: {e}", exc_info=True)
    finally:
        connection.close()
    

