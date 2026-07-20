import modal
import subprocess

apollo_image = modal.Image.debian_slim().apt_install("wget", "unzip", "libvulkan1").run_commands(
    "wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip",
    "unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip -d /realesrgan",
    "chmod +x /realesrgan/realesrgan-ncnn-vulkan"
)

app = modal.App()

@app.function(image=apollo_image, gpu="T4")
def test_upscale():
    # Test if the binary runs
    result = subprocess.run(["/realesrgan/realesrgan-ncnn-vulkan", "-h"], capture_output=True, text=True)
    print(result.stdout)
    if "realesrgan-ncnn-vulkan" in result.stdout:
        print("SUCCESS! Binary runs.")
    else:
        print("FAILED:", result.stderr)
