import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    image = Image.open(image_path)
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.5)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.SHARPEN)
    return image

def extract_text(image_path):
    image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
    return text

def parse_citizenship(text):
    data = {
        'full_name': '',
        'citizenship_number': '',
        'date_of_birth': '',
        'district': '',
        'raw_text': text,
    }

    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # ── Full Name ──
        # Matches: "full name : John Doe" or "full name: John Doe"
        if 'full name' in line_lower:
            parts = re.split(r'[:\-]', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                data['full_name'] = parts[1].strip()
            elif i + 1 < len(lines):
                data['full_name'] = lines[i + 1].strip()

        # ── Citizenship / Driving Number ──
        # Matches: "citizen no:" or "driving no:"
        if any(keyword in line_lower for keyword in ['citizen no', 'citizenship no', 'driving no', 'license no']):
            parts = re.split(r'[:\-]', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                data['citizenship_number'] = parts[1].strip()
            elif i + 1 < len(lines):
                data['citizenship_number'] = lines[i + 1].strip()

        # Also try to find number pattern anywhere in line
        if not data['citizenship_number']:
            match = re.search(r'\b\d{2,3}[-/]\d{2,3}[-/]\d{4,8}\b', line)
            if match:
                data['citizenship_number'] = match.group()

        # ── Date of Birth ──
        # Matches: "date of birth(dob):" or "dob:"
        if any(keyword in line_lower for keyword in ['date of birth', 'dob', 'd.o.b']):
            parts = re.split(r'[:\-]', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                data['date_of_birth'] = parts[1].strip()
            elif i + 1 < len(lines):
                data['date_of_birth'] = lines[i + 1].strip()

        # Also search for date pattern anywhere
        if not data['date_of_birth']:
            match = re.search(
                r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
                line
            )
            if match:
                data['date_of_birth'] = match.group()

        # ── District ──
        # Matches: "district:"
        if 'district' in line_lower:
            parts = re.split(r'[:\-]', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                data['district'] = parts[1].strip()
            elif i + 1 < len(lines):
                data['district'] = lines[i + 1].strip()

    return data