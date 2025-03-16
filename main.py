# from detect_copy import *
from detect import *
from translate import *
from place_text import *
from handle_table import *
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, SafetySetting
import os
import tempfile
import gradio as gr

    
def main(save_pdf, pdf_file,chosen_model,translate_table='False'):
    # save_pdf = save_pdf + ".pdf"
    vertexai.init(project="dla-presales-team-sandbox", location="us-central1")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "presales_cred.json"
    if chosen_model == "RCNN X101":
        model_ocr = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6], #Convidance
                                        label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    elif chosen_model == "RCNN R50":
        model_ocr = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_R_50_FPN_3x/config',
                                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                        label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    elif chosen_model == "Fast RCNN R50":
        model_ocr = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                        label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    else:
        model_ocr = lp.Detectron2LayoutModel('lp://PrimaLayout/mask_rcnn_R_50_FPN_3x/config',
                                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                        label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    model = GenerativeModel(model_name="gemini-2.0-flash-001")
    generation_config = {
            "max_output_tokens": 3000,
            "temperature": 0.8,
            "top_p": 0.95,
        }
    # if translate_table == 'True':
    #     file = replace_table_with_image(pdf_file, 'temp.pdf')
    #     pdf_file = 'temp.pdf'
    text_data, shape = bounding_box(pdf_file, model_ocr, translate_table)
    print("SUCCESS OCR")
    # print(text_data)

    translated = translate(model,generation_config,text_data)
    print("SUCCESS TRANSLATED")
    file = annotate_pdf_multiple(pdf_file, save_pdf, translated, shape)
    ret = f"File saved to {save_pdf}"
    print(ret)
    return file

with gr.Blocks() as demo:
    with gr.Row():
        title = gr.HTML("<h1>Document Translator</h1>")
    with gr.Row():
        with gr.Column():
            pdf_file = gr.UploadButton(file_types=[".pdf"])
            save_pdf = gr.Textbox(label="Result Pdf File Name")
            trans_table=gr.Dropdown(["True", "False"], label="Translate table")
            chosen_model = gr.Dropdown(choices=["RCNN X101","RCNN R50", "Fast RCNN R50", "P RCNN R50"], label="ocr_model", info="Choose OCR Model")
        with gr.Column():
            translate_btn = gr.Button(value="Translate Document")
            translate_btn.click(fn=main, inputs = [save_pdf,pdf_file,chosen_model,trans_table], outputs=gr.File(label="Download Annotated PDF", file_types=[".pdf"]))

if __name__ == "__main__":      
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_port=port, server_name="0.0.0.0")
    
