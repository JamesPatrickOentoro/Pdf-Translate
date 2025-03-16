
# Ensure correct service account JSON path

from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import time
from tqdm import tqdm
import re
import io
def translate(model,generation_config,contents):

    

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


    # new_contents = []
    for i,content in enumerate(contents):
        time.sleep(2)
        # print(i, 'IIIIIII')
        if content['text'] == None or content['text'] == '':
            continue
        prompt = ["You are a translator, your job is to translate texts to indonesian, ONLY ANSWER WITH THE TRANSLATION WITHOUT INTRODUCTION, DO NOT ERASE THE NUMBERINGS FROM THE TEXT BUT TRANSLATE THE TEXT TO INDONESIAN:", content['text']]
        responses = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )

        
        # print(responses,'RESPONSES')
        contents[i]['translated'] = responses.text
        # print(content,'CONTENT')
        # new_contents.append(content)
    # print(len(contents),"LENNNNN")
        
        
    # print(new_contents,'NEW CONTENTS')
    for item in contents:
        if item['type'] == 'List':
            normalized_text = re.sub(r'\n+', '\n', item['translated'])
            lines = normalized_text.splitlines()
            bulleted_lines = []
            for line in lines:
                if not re.match(r'^\d+\.?\s*', line):  # Check if line starts with a number
                    bulleted_lines.append(f"- {line.strip()}")
                else:
                    bulleted_lines.append(line.strip())  # Keep the line as is
            item['translated'] = "\n".join(bulleted_lines)

    # print(f"Total Execution Time: {total_execution_time:.2f} seconds")
    # if first_token_latency is not None:
        # print(f"Time to First Token: {first_token_latency:.2f} seconds")
    print(contents,'NEW_CONTENTS')
    return contents


def translate_table(pil_image):
    # Set safety settings
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
    
    # Initialize the model
    model = GenerativeModel(model_name="gemini-2.0-flash-001")
    
    # Prepare generation config
    generation_config = {
        "max_output_tokens": 3000,
        "temperature": 0.8,
        "top_p": 0.95,
    }
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Define the prompt
    prompt = f"You are an english to indonesian table translator, translate the table in the image and generate a new translated table in HTML format.  Answer only with the HTML without explanation"
    
    # Create the parts using the from_text and from_data methods
    prompt_part = Part.from_text(prompt)  # Use from_text for the prompt
    image_part = Part.from_data(img_byte_arr, mime_type="image/png")  # Use from_data for the image
    
    # Combine parts
    contents = [prompt_part, image_part]
    
    # Call model to generate response
    responses = model.generate_content(
        contents=contents,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    
    # Return the generated response text (HTML content)
    # print(responses.text,'HASILLLL')
    return responses.text
