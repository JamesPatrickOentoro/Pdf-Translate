import pdf2image
import numpy as np
import layoutparser as lp
import PIL
import json
import fitz
import time
import re
from io import BytesIO
from vertexai.preview.generative_models import GenerativeModel, Part, SafetySetting

def gemini_bounding_box(img_path):
    model = GenerativeModel(model_name="gemini-2.0-flash-001")
    generation_config = {
            "max_output_tokens": 8192,
            "temperature": 0.8,
            "top_p": 0.95,
        }
    try:
        with open(img_path, "rb") as image_file: #open file in binary read mode
            image_bytes = image_file.read() #read bytes
    except FileNotFoundError:
        print(f"Error: Image file '{img_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading image: {e}")
        return None
    
    contents = [Part.from_data(
            data=image_bytes,
            mime_type="image/jpg"
        ),
        "Detect Paragraphs that contains texts, Titles, Lists, Tables, and Figures. Output a dictionary list where each entry contains the 2D bounding box in 'loc' in the format of [x0,y0,x1,y1],a label in 'label' consisting one of ['Paragraph', 'Title', 'List', 'Table' ,'Figure'], and the text containing in the bounding box in 'text'. ",
        "Do not make an overlaping bounding box, if the label is 'Table' or 'Figure' no need to return the 'text' inside",
        """SAMPLE OUTPUT: [
  {"loc": [x0, y0, x1, y1], "label": "Title", "Text":"How to eat a banana"},
  {"loc": [x0, y0, x1, y1], "label": "Paragraph", "Text":"First peal off the banana"},
  {"loc": [x0, y0, x1, y1], "label": "Table"}
]"""]
    safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
    ]

    responses = model.generate_content(
    contents,
    generation_config=generation_config,
    safety_settings=safety_settings,
    stream=False)

    
    raw_response = responses.text

    match = re.search(r"\[.*\]", raw_response, re.DOTALL) # Find JSON array
    if match:
        json_string = match.group(0)
        try:
            data = json.loads(json_string)
            # print(data)
            return data, image_bytes
        except json.JSONDecodeError as e:
            print(f"JSON Error after regex extraction: {e}")
            return None
    else:
        print("No JSON found in response.")
        return None
    


# def bounding_box(pdf_file, model, save_name):
#     page_text = []

#     doc = fitz.open(pdf_file)  # Open PDF with PyMuPDF

#     for page_num in range(doc.page_count):
#         page = doc[page_num]
#         pix = page.get_pixmap()
#         width = pix.width
#         height = pix.height
#         shape = (height, width)
#         # Convert the image to bytes.  Important for Gemini
#         img_bytes = pix.tobytes()

#         results = gemini_bounding_box(img_bytes)
#         # print(results,"RESSSSSSSSS")
#         for result in results:
#             if isinstance(result, dict) and 'label' in result and result['label'] in ('Title', 'List', 'Paragraph'):
#                 result['page'] = page_num
#                 page_text.append(result)
#     print(page_text, 'TO BE TRANSLATED')
#     return page_text, shape



def bounding_box_gemini(img_path):

    page_text = []
    results, image_bytes = gemini_bounding_box(img_path)
    for result in results:
        if isinstance(result, dict) and 'label' in result and result['label'] in ('Title', 'List', 'Paragraph'):
            page_text.append(result)
    print(page_text, 'TO BE TRANSLATED')
    return page_text, image_bytes