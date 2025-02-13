import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()

from django.conf import settings
from docx import Document


def get_highlighted_text(doc):
    highlighted_text = []

    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.highlight_color:  # Check if the text is highlighted
                highlighted_text.append((run.text, run.font.highlight_color))

    return highlighted_text


if __name__ == "__main__":
    ad_scripts_folder = os.path.join(settings.BASE_DIR, 'ad_scripts')
    doc_path = os.path.join(ad_scripts_folder, 'Youtube Edit - 08.11.24 DM - 0558JE - 0699MA - 0558JE Intro .docx')
    doc = Document(doc_path)

    # Extract text
    text = "\n".join([para.text for para in doc.paragraphs])

    # Highlighted
    highlighted_content = get_highlighted_text(doc=doc)

    # Print extracted highlighted text with its color
    for text, color in highlighted_content:
        print(f"Highlighted Text: '{text}' | Color: {color}")


