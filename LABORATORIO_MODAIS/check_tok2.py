import modal
app = modal.App("fish-tokenizer-check")
fish_image = modal.Image.debian_slim(python_version="3.11").pip_install("transformers", "tiktoken", "sentencepiece", "protobuf")
@app.function(image=fish_image)
def check_tokenizer():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("fishaudio/fish-speech-1.5")
    return list(tok.get_added_vocab().keys())
@app.local_entrypoint()
def main():
    print(check_tokenizer.remote())
