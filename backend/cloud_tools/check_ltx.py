import modal
from apollo_modal_engine import apollo_image

app = modal.App()

@app.function(image=apollo_image)
def check_ltx():
    import inspect
    from diffusers import LTXVideoPipeline
    print("LTXVideoPipeline signature:")
    print(inspect.signature(LTXVideoPipeline.__call__))
    try:
        from diffusers import LTX2Pipeline
        print("LTX2Pipeline signature:")
        print(inspect.signature(LTX2Pipeline.__call__))
    except:
        pass
