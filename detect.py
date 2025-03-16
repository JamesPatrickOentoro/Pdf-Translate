import pdf2image
import numpy as np
import layoutparser as lp
import PIL.Image
import os
from translate import *
from PIL import Image, ImageDraw
# --- End of custom draw_box function ---
from PIL import Image
PIL.Image.LINEAR = PIL.Image.BILINEAR

# ... (your code for loading the PDF and models) ...

def bounding_box(pdf_file, model, translate_table, output_folder="segmented_images"):
    images  = pdf2image.convert_from_path(pdf_file)
    print(len(images), 'LEMBARRR')
    page_text = []
    for i in range(len(images)):
        img = np.asarray(images[i])


        layout_result = model.detect(img)


        # --- Use YOUR draw_box function here! ---
        # img_with_layout = lp.draw_box(PIL.Image.fromarray(img), layout_result, box_width=5, box_alpha=0.2, show_element_type=True)
        # img_with_layout.save(f'{save_name}{i}.png')  # Save the image


        print("Layouts saved!")

        text_blocks = lp.Layout([
            block for block in layout_result._blocks if block.type in ["Text", "Title", "List","Table"]
        ])
        image_width = len(img[0])

        # Sort element ID of the left column based on y1 coordinate
        left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(img)
        left_blocks = text_blocks.filter_by(left_interval, center=True)._blocks
        left_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort element ID of the right column based on y1 coordinate
        right_blocks = [b for b in text_blocks if b not in left_blocks]
        right_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort the overall element ID starts from left column
        text_blocks = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])
        ocr_agent = lp.TesseractAgent(languages='eng')

        for block in text_blocks:
            if block.type == 'Table':
                if translate_table == 'True':
                    segment_image = (block
                                    .pad(left=15, right=15, top=5, bottom=5)
                                    .crop_image(img))

                    # Add white background to the padded area
                    segment_pil_image = Image.fromarray(segment_image)
                    draw = ImageDraw.Draw(segment_pil_image)
                    width, height = segment_pil_image.size
                    draw.rectangle((0, 0, width, height), fill=(255, 255, 255)) # Fill with white

                    #paste the cropped image onto the white background.
                    cropped_pil_image = Image.fromarray(block.crop_image(img))
                    left_pad = 15
                    top_pad = 5
                    segment_pil_image.paste(cropped_pil_image,(left_pad,top_pad))

                    # Save cropped table img
                    output_filename = f"page_{i}_block_{block.id}_{block.type}.png"
                    output_path = os.path.join(output_folder, output_filename)
                    segment_pil_image.save(output_path)
                    print(f"Saved segment image: {output_path}")

                    html = translate_table(segment_pil_image)
                    print(html,'HTMLLL')
                    block.set(text=html, inplace=True)
                    print(block.text,'BLOCKKK')
            else:
                # Crop image around the detected layout
                segment_image = (block
                                .pad(left=15, right=15, top=5, bottom=5)
                                .crop_image(img))
                
                # Perform OCR
                text = ocr_agent.detect(segment_image)
                
                # Save OCR result
                block.set(text=text, inplace=True)

        
        for txt in text_blocks:
            # print("Text = ",txt.text)
            # print("x_1=",txt.block,end='\n---\n')
            # print(txt)
            page_text.append({"text":txt.text,
                            "loc":txt.block,
                            'page':i,
                            'type':txt.type})
        
            
    return page_text, img.shape


















