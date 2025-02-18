import fitz  # PyMuPDF
import PIL.Image
import io
import numpy as np
import tempfile
import time
import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


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


# def annotate_pdf_multiple(input_pdf, output_pdf, annotations, img_shape):
#     """Annotate a PDF with multiple text boxes, correctly handling coordinate conversion."""
#     doc = fitz.open(input_pdf)
#     for i in range(doc.page_count):  # Assuming you're working with the first page. Adjust if needed.
#         doc = fitz.open(input_pdf)
#         pdf_width = doc[i].rect.width
#         pdf_height = doc[i].rect.height
#         filtered_data = [item for item in annotations if item["page"] == i]
#         for annotation in filtered_data:
#             bbox_image = annotation['loc']  # Bounding box in image coordinates
#             text = annotation['translated']

#             # Convert image coordinates to PDF coordinates
#             x0 = (bbox_image.x_1 / img_shape[1]) * pdf_width  # Use img_shape[1] for width
#             y0 = (bbox_image.y_1 / img_shape[0]) * pdf_height # Use img_shape[0] for height
#             x1 = (bbox_image.x_2 / img_shape[1]) * pdf_width
#             y1 = (bbox_image.y_2 / img_shape[0]) * pdf_height

#             bbox_pdf = (x0, y0, x1, y1)
#             rect = fitz.Rect(*bbox_pdf)

#             # Draw white background (optional, but often helpful)
#             doc[i].draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

#             fontsize = 12  # Start with a reasonable font size

#             rc = doc[i].insert_textbox(
#                 rect,
#                 text,
#                 fontname="helv",  # Or any available font
#                 fontsize=fontsize,
#                 color=(0, 0, 0),  # Black text
#                 align=0  # Adjust alignment as needed
#             )

#             # Handle text overflow (important!)
#             if rc < 0:
#                 print(f"Warning: Text overflow in bbox {bbox_image} on page 0. Reducing font size.")
#                 while rc < 0 and fontsize > 2: # Loop to reduce font size until text fits.
#                     fontsize -= 0.5
#                     rc = doc[i].insert_textbox(
#                         rect,
#                         text,
#                         fontname="helv",  # Or any available font
#                         fontsize=fontsize,
#                         color=(0, 0, 0),  # Black text
#                         align=0  # Adjust alignment as needed
#                     )

#                 if rc < 0:
#                     print(f"Error: Text still overflows after reducing font size. Text: {text[:20]}...")
#         time.sleep(2)
#     doc.save(output_pdf)
#     doc.close()



def annotate_pdf_multiple(pdf_file, output_file, annotations, img_shape):
    
    doc = fitz.open(pdf_file.name)
    print(annotations)
    for page_num in range(doc.page_count):
        page = doc[page_num]
        # annotations_for_page = translated.get(page_num, [])  # Get annotations for this page

        
        pdf_width = page.rect.width
        pdf_height = page.rect.height
        
        # print(filtered_data, 'FILTERED DATA PER PAGE')
        annotations_page = [i for i in annotations if i['page']==page_num]
        # print(annotations_page,'ANNOTATIONSSSSS')
        for annotation in annotations_page:
            bbox_image = annotation['loc']
            text = annotation['translated']

            # x0 = (bbox_image[1] / img_shape[0]) * pdf_width
            # y0 = (bbox_image[0] / img_shape[1]) * pdf_height
            # x1 = (bbox_image[3] / img_shape[0]) * pdf_width
            # y1 = (bbox_image[2] / img_shape[1]) * pdf_height

            x0 = (bbox_image.x_1 / img_shape[1]) * pdf_width #traditional detect
            y0 = (bbox_image.y_1 / img_shape[0]) * pdf_height
            x1 = (bbox_image.x_2 / img_shape[1]) * pdf_width
            y1 = (bbox_image.y_2 / img_shape[0]) * pdf_height
            # print(f"Rect coordinates: x0={x0}, y0={y0}, x1={x1}, y1={y1}")
            bbox_pdf = (x0, y0, x1, y1)
            rect = fitz.Rect(*bbox_pdf)

            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            fontsize = 12
            while True:  # Font size adjustment loop
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
    # doc.save(output_file)  # Save the modified document
    # doc.close()
    annotated_pdf_bytes = doc.tobytes()  # Get PDF bytes
    doc.close()
    temp_file_path = os.path.join(tempfile.gettempdir(), output_file + ".pdf")
    with open(temp_file_path, "wb") as temp_file:
            temp_file.write(annotated_pdf_bytes)

    return temp_file_path
    
def annotate_png(png_file, output_file, annotations, image_bytes):
    """Annotates a PNG image with bounding boxes and text, scaled correctly."""
    try:
        # 1. Decode the bytes into a PIL Image:
        image_file = io.BytesIO(image_bytes)  # Use BytesIO to treat bytes as a file
        img = Image.open(image_file).convert("RGB")
        png_width, png_height = img.size
    except Exception as e:
        print(f"Error decoding image bytes: {e}")
        return None  # Or raise the exception if you prefer

    draw = ImageDraw.Draw(img)

    for i,annotation in enumerate(annotations):
        bbox_pdf = annotation.get('loc')  # Coordinates from Gemini (likely PDF-based)
        text = annotation.get('translated', "")  # Handle missing 'text' for Tables/Figures
        label = annotation.get('label')

        if not bbox_pdf: #handle if bbox is None
            continue

        y0_pdf, x0_pdf, y1_pdf, x1_pdf = bbox_pdf

        # Assuming Gemini's coordinates are relative to a PDF of a certain size.
        # You'll need to determine the original PDF width and height that Gemini uses.
        # This might involve inspecting Gemini's output or making an educated guess.
        # If Gemini doesn't specify PDF size, you may have to assume that the PDF size is the size of the PNG file or experiment with different scaling factors.

        # Example: if the PDF width and height are the same as the PNG width and height
        pdf_width = png_width
        pdf_height = png_height

        # Calculate scaling factors
        x_scale = png_width / pdf_width *3.1
        y_scale = png_height / pdf_height *3.1

        # Scale the bounding box coordinates
        x0_png = int(x0_pdf * x_scale) - (i*15)
        y0_png = int(y0_pdf * y_scale) + (i*15)
        x1_png = int(x1_pdf * x_scale) - (i*15)
        y1_png = int(y1_pdf * y_scale) + (i*15)

        print(f"PNG coordinates: x0={x0_png}, y0={y0_png}, x1={x1_png}, y1={y1_png}")

        # Draw the rectangle
        draw.rectangle((x0_png, y0_png, x1_png, y1_png), outline=(255, 255, 255), fill=(255, 255, 255))

        # Add text (if available and not a Table/Figure)
        if text and label not in ("Table", "Figure"):
            fontsize = 50
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", fontsize)  # Correct font path
            text_bbox = draw.textbbox((x0_png, y0_png), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            while text_width > (x1_png - x0_png) or text_height > (y1_png - y0_png):
                fontsize -= 1
                font = ImageFont.truetype("/Library/Fonts/Arial.ttf", fontsize)  # Correct font path
                text_bbox = draw.textbbox((x0_png, y0_png), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                if fontsize < 2:
                    print(f"Error: Text overflows. Text: {text[:20]}...")
                    break

            draw.text((x0_png, y0_png), text, fill=(0, 0, 0), font=font)

    img.save(output_file)
    img.close()



