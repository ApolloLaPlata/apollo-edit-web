import modal
app = modal.App("test-vol")

@app.function(volumes={"/data": modal.Volume.from_name("apollo-voice-models")})
def check_vol():
    import os
    print("Contents of /data:", os.listdir("/data"))
    if os.path.exists("/data/fish-speech-1.5"):
        print("Contents of /data/fish-speech-1.5:", os.listdir("/data/fish-speech-1.5"))

@app.local_entrypoint()
def main():
    check_vol.remote()
