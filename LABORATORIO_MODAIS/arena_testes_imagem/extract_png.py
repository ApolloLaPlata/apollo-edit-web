import json
from PIL import Image

def extract_workflow(image_path):
    img = Image.open(image_path)
    if "prompt" in img.info:
        with open("workflow.json", "w") as f:
            f.write(img.info["prompt"])
        print("Prompt extraido!")
    if "workflow" in img.info:
        with open("workflow_ui.json", "w") as f:
            f.write(img.info["workflow"])
        print("Workflow UI extraido!")

extract_workflow("E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\arena_testes_imagem\\z_image_turbo_example.png")
