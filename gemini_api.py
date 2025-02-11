import os
import grpc
import django
import pandas as pd
import google.generativeai as genai


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()


# Gemini API config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Load Excel File with Ad Ideas
def load_ad_ideas(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
    return df

# Generate Ad Scripts Using Gemini AI
def generate_ad_script(ad_idea):
    prompt = f"""
    Create a compelling advertising script based on the following idea:
    {ad_idea}

    The script should be engaging, persuasive, and include a strong call to action.
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    grpc.Channel.close = lambda self: None
    return response.text if response else "No response from AI."

# Process Ad Ideas and Generate Scripts
def process_ads(file_path, output_csv="generated_ads.csv"):
    df = load_ad_ideas(file_path)
    
    if "Idea" not in df.columns:
        print("Error: Excel file must have a column named 'Idea'.")
        return

    df["Generated Script"] = df["Idea"].apply(generate_ad_script)
    df.to_csv(output_csv, index=False)
    print(f"Ad scripts saved to {output_csv}")


if __name__ == '__main__':
    process_ads("test_ad_ideas.xlsx")
