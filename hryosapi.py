import os
import json
import django
import requests


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()


# Config
HYROS_API_KEY = os.environ.get("HYROS_API_KEY")
HEADERS = {
  'API-Key': HYROS_API_KEY
}
INTEGRATIONS = ['FACEBOOK', 'GOOGLE', 'SNAPCHAT', 'TIKTOK', 'TWITTER', 'LINKEDIN']
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(ROOT_DIR, 'output')
os.makedirs(OUTPUT_PATH, exist_ok=True)


class FetchHyrosData:
    def __init__(self):
        pass

    # Fetch data Hyros API
    def fetch_hyros_data(self, url, params=None):
        response = requests.get(url=url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None


    # Save data as a JSON file
    def save_as_json(self, data, filename):
        file_path = os.path.join(OUTPUT_PATH, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


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
                    print("API request sent")
                    self.save_as_json(data=data, filename=f"{filename}.json")
                    print("Data saved as JSON successfully!")
                else:
                    print("Failed to fetch data.")

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
                    print("API request sent")
                    self.save_as_json(data=data, filename=f"{filename}.json")
                    print("Data saved as JSON successfully!")
                else:
                    print("Failed to fetch data.")

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
                print("API request sent")
                self.save_as_json(data=data, filename=f"{filename}.json")
                print("Data saved as JSON successfully!")
            else:
                print("Failed to fetch data.")

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
                print("API request sent")
                self.save_as_json(data=data, filename=f"{filename}.json")
                print("Data saved as JSON successfully!")
            else:
                print("Failed to fetch data.")

            if pageId is None:
                next_page = False
            num += 1


if __name__ == "__main__":
    hyros = FetchHyrosData()

