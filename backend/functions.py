import re
import fitz
import pytesseract
from PIL import Image
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def safe_parse_json(text: str) -> dict:
    if not text:
        return {}

    # Remove markdown code fences
    cleaned = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    # Extract JSON object only
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")

    return json.loads(match.group())

def pdf_to_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)
    images = []

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    logger.info(f"Total pages: {len(images)}")
    return images

def pan_and_user_pg_num(pages):
    PAN_KEYWORDS = [
            "पैन", "पीएएन", "स्थायी लेखा", "स्थायी लेखा संख्या", "Permanent Account", "PAN"
        ]
    USER_DETAILS_KEYWORDS = [
        "नाम-निर्देशन", "नाम निर्देशन पत्र", "निर्वाचन क्षेत्र", "विधान सभा", "शपथ", "आयु", "पिता", "पति", "निवासी", "राज्य", "जिला", "वित्तीय वर्ष", "आयकर", "शपथ पत्र", "राजनीतिक दल", "स्वतंत्र",
    ]
    pan_page = None
    user_details_page = None
    
    for idx, page in enumerate(pages):
        text = pytesseract.image_to_string(
            page,
            lang="hin+eng",
            config="--psm 6"
        )
        text_lower = text.lower()

        if pan_page is None and any(k.lower() in text_lower for k in PAN_KEYWORDS):
            logger.info(f"PAN page detected at page {idx + 1}")
            pan_page = idx

        if user_details_page is None and any(k.lower() in text_lower for k in USER_DETAILS_KEYWORDS):
            logger.info(f"User details page detected at page {idx + 1}")
            user_details_page = idx
        
        if pan_page is not None and user_details_page is not None:
            break
        
    if pan_page is None:
        logger.error("PAN page not found in the document")
        raise Exception("PAN page not found")

    if user_details_page is None:
        logger.error("User details page not found in the document")
        raise Exception("User details page not found")

    return pan_page, user_details_page
    
def get_user_details(pages, page_index):
    first_page_image = pages[page_index]
    user_prompt = """
    This is the FIRST PAGE of an Indian affidavit.

    Extract ONLY the following user details if present:
    1. Full Name
    3. Address (full)
    4. Phone Number (if mentioned)
    6. Age (if mentioned)
    
    Convert the details from hindi to english if they are in hindi.
    Return STRICT JSON only:
    {
      "name": "...",
      "age": "...",
      "address": "...",
      "phone": "..."
    }

    Rules:
    - Return null for any missing field.
    - Ensure JSON is valid.
    """
    logger.info("Extracting user details from user details page...")
    try:
        user_response = model.generate_content([user_prompt, first_page_image])
    except Exception as e:
        logger.error("Error during user details extraction:", str(e))
        return {}
    logger.info("User Details Raw:")
    logger.info(user_response.text)

    return safe_parse_json(user_response.text)

def get_pan_number_details(pages, pan_page_index, user_data):
    pan_page_image = pages[pan_page_index]

    pan_prompt = """
    This is a PAN-related page from an Indian affidavit.

    Extract ONLY the PAN card number.
    PAN format: AAAAA9999A

    Rules:
    - PAN is usually below headings like:
      "पीएएन", "स्थायी लेखा", "स्थायी लेखा संख्या"
    - Return ONLY the PAN string
    - If not visible, return null
    """

    logger.info("Extracting PAN from PAN page...")
    try:
        pan_response = model.generate_content([pan_prompt, pan_page_image])
    except Exception as e:
        logger.error("Error during PAN extraction:", str(e))
        return user_data
    logger.info("PAN Raw Result:")
    logger.info(pan_response.text)
    chq_pan_number(pan_response.text, user_data)
    return user_data
    
    
def chq_pan_number(pan_number, user_data):
    pan_text = re.sub(r"```json|```", "", pan_number, flags=re.IGNORECASE).strip()

    if pan_text.lower() == "null":
        pan_value = None
    else:
        pan_value = pan_text.strip('"').strip()

    def is_valid_pan(pan):
        return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan or ""))

    if not is_valid_pan(pan_value):
        pan_value = None

    user_data["pan"] = pan_value



# pdf_path = "affidavit3.pdf"

def process_pdf(pdf_path):
    pages = pdf_to_images(pdf_path)
    pan_page, user_page = pan_and_user_pg_num(pages)
    user_data = get_user_details(pages, user_page)
    result = get_pan_number_details(pages, pan_page, user_data)
    logger.info("\n FINAL MERGED JSON:")
    logger.info(json.dumps(result, indent=2))
    return result