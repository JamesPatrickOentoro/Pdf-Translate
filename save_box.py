from detect_copy import *
import json
import re
from PIL import Image, ImageDraw


def draw_bounding_boxes(image_bytes, data):
    """Draws bounding boxes on the image and returns the modified image."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB") #convert to RGB to avoid error in draw.rectangle if image is in RGBA
        draw = ImageDraw.Draw(image)

        if data:
            for item in data:
                try:  # Handle potential issues with individual bounding boxes
                    loc = item.get("loc")
                    label = item.get("label")
                    text = item.get("text")


                    if loc:
                        x0, y0, x1, y1 = loc
                        draw.rectangle([x0, y0, x1, y1], outline="red", width=2)  # Draw the rectangle

                        # Add label and text (if available and not a table/figure)
                        label_text = label
                        if text and label not in ("Table", "Figure"):
                            label_text += ": " + text[:50] #limit the text to 50 character to prevent long text
                        
                        # Calculate a suitable position for the text (adjust as needed)
                        text_x = x0
                        text_y = y0 - 50  # Position text slightly above the box
                        draw.text((text_x, text_y), label_text, fill="red")

                except (TypeError, ValueError, KeyError) as e:
                    print(f"Error processing bounding box: {e}. Item: {item}")
                    continue #skip the current bounding box and proceed to the next one

        return image

    except Exception as e:
        print(f"Error drawing bounding boxes: {e}")
        return None



import io #import io for handling bytes stream

# Example usage:
img_path = "SOP Manual/sample_pages_with_table_3.jpg"  # Replace with your image path
result, image_bytes = gemini_bounding_box(img_path)

if result and image_bytes:
    image_with_boxes = draw_bounding_boxes(image_bytes, result)

    if image_with_boxes:
        # Save the image with bounding boxes
        output_path = "image_with_boxes.png"  # Or any other desired path
        image_with_boxes.save(output_path)
        print(f"Image with bounding boxes saved to {output_path}")
    else:
        print("Failed to draw bounding boxes.")
else:
    print("Failed to get bounding box data.")