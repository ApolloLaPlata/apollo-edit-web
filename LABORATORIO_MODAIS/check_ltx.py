import modal

app = modal.App("apollo-check-ltx")

@app.function(image=modal.Image.debian_slim(python_version="3.10").apt_install("git").pip_install("git+https://github.com/huggingface/diffusers.git", "torch", "transformers"))
def check():
    from diffusers import LTX2Pipeline
    import inspect
    print("ASSINATURA:")
    print(inspect.signature(LTX2Pipeline.__call__))

if __name__ == "__main__":
    with app.run():
        check.remote()
