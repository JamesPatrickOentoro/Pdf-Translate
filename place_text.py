import fitz
import imgkit
from PIL import Image
import io
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader
import os

def find_optimal_fontsize(page, rect, text, max_fontsize=100, min_fontsize=4):
    """Binary search for optimal font size that fits in the bounding box"""
    best_size = min_fontsize
    low, high = min_fontsize, max_fontsize
    
    while low <= high:
        mid = (low + high) // 2
        # Test if text fits with current font size
        rc = page.insert_textbox(
            rect,
            text,
            fontname="helv",
            fontsize=mid,
            color=(0, 0, 0),
            align=0
        )
        
        if rc > 0:
            best_size = mid
            low = mid + 1  # Try larger sizes
        else:
            high = mid - 1  # Reduce size
            
    return best_size



# def annotate_pdf_multiple(input_pdf, output_pdf, annotations):
#     """
#     Annotate a PDF with multiple text boxes with white backgrounds.
    
#     Parameters:
#         input_pdf (str): Input PDF file path
#         output_pdf (str): Output PDF file path
#         annotations (list): List of dictionaries containing:
#             - 'bbox': (x1, y1, x2, y2) coordinates
#             - 'text': Text to insert
#             - 'page_num': Page number (0-based, optional, default=0)
#             - 'fontsize': Font size (optional, default=12)
#     """
#     doc = fitz.open(input_pdf)
    
#     for annotation in annotations:
#         page_num = annotation.get('page_num', 0)
#         bbox = (annotation['loc'][0]/2.2,annotation['loc'][1]/2.2,annotation['loc'][2]/2.2,annotation['loc'][3]/2.2)
#         text = annotation['translated']
        
        
#         page = doc[page_num]
#         rect = fitz.Rect(*bbox)
        
#         # Draw white background
#         page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
#         # Fit text to box using a loop to adjust font size
#         fontsize = 10

#         rc = page.insert_textbox(
#             rect,
#             text,
#             fontname="helv",
#             fontsize=fontsize,
#             color=(0, 0, 0),
#             align=0
#         )
        
#         if rc < 0:
#             print(f"Warning: Text overflow in bbox {bbox} on page {page_num}")

#     doc.save(output_pdf)
#     doc.close()


def annotate_pdf_from_boxes(input_pdf, output_pdf, page_text):
    """Annotate PDF using detected text and boxes from bounding_box()"""
    doc = fitz.open(input_pdf)
    
    for annotation in page_text:
        page = doc[0]  # Assuming first page, modify if needed
        x1, y1, x2, y2 = annotation["loc"]
        rect = fitz.Rect(x1, y1, x2, y2)
        
        # Draw white background
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Insert text
        rc = page.insert_textbox(
            rect,
            annotation["text"],
            fontname="helv",
            fontsize=12,  # Adjust based on box height if needed
            color=(0, 0, 0),
            align=0
        )

    doc.save(output_pdf)
    doc.close()

import fitz  # PyMuPDF
import os
import tempfile

def annotate_pdf_multiple(pdf_file, output_file, annotations, img_shape):
    print('MASUK ANNOTATE')
    doc = fitz.open(pdf_file)

    for page_num in range(doc.page_count):
        page = doc[page_num]

        pdf_width = page.rect.width
        pdf_height = page.rect.height

        annotations_page = [i for i in annotations if i['page'] == page_num]

        for annotation in annotations_page:
            if annotation['type'] == 'Table':
                html_string = annotation['text']  # HTML string from annotation
                bbox_image = annotation['loc']

                # Calculate bounding box for the table
                x0 = (bbox_image.x_1 / img_shape[1]) * pdf_width
                y0 = (bbox_image.y_1 / img_shape[0]) * pdf_height
                x1 = (bbox_image.x_2 / img_shape[1]) * pdf_width
                y1 = (bbox_image.y_2 / img_shape[0]) * pdf_height

                bbox_pdf = (x0, y0, x1, y1)
                rect = fitz.Rect(*bbox_pdf)
                html_string_with_bg = f'''
                    <div style="background-color: white;">
                        <style>
                            table, th, td {{
                                border: 1px solid black;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                padding: 5px;
                                text-align: left;
                            }}
                        </style>
                        {html_string}
                    </div>
                '''
                rc = page.insert_htmlbox(rect, html_string_with_bg)

            else:
                bbox_image = annotation['loc']
                text = annotation['translated']

                # Calculate bounding box for text
                x0 = (bbox_image.x_1 / img_shape[1]) * pdf_width
                y0 = (bbox_image.y_1 / img_shape[0]) * pdf_height
                x1 = (bbox_image.x_2 / img_shape[1]) * pdf_width
                y1 = (bbox_image.y_2 / img_shape[0]) * pdf_height

                bbox_pdf = (x0, y0, x1, y1)
                rect = fitz.Rect(*bbox_pdf)

                # Draw a white rectangle to clear the area (if needed)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

                # Adjust the font size until the text fits
                fontsize = 12
                while True:
                    rc = page.insert_textbox(
                        rect,
                        text,
                        fontname="helv",
                        fontsize=fontsize,
                        color=(0, 0, 0),
                        align=0
                    )
                    if rc >= 0:
                        break
                    fontsize -= 0.5
                    if fontsize < 2:
                        print(f"Error: Text still overflows after reducing font size. Text: {text[:20]}... on page {page_num}")
                        break

    # Save the annotated PDF to a temporary file and return the path
    annotated_pdf_bytes = doc.tobytes()  # Get PDF bytes
    doc.close()

    temp_file_path = os.path.join(tempfile.gettempdir(), output_file + ".pdf")
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(annotated_pdf_bytes)

    return temp_file_path





