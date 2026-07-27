import modal
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engines.flux_txt2img_engine import Flux2Txt2ImgEngine
from modal_app import app

@app.local_entrypoint()
def main():
    engine = Flux2Txt2ImgEngine()
    print("Testing Flux2Txt2ImgEngine remote...")
    res = engine.generate.remote(prompt="A cute cat", aspect_ratio="square")
    print(res)
