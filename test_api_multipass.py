import requests
import json
import base64
import sys

def test_api():
    url = "http://localhost:8080/api/studio/modal/generate_image"
    
    # Send a dummy base64 string
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    payload = {
        "prompt": "Test multipass with two characters on a bench",
        "model": "flux2-universal",
        "reference_images_base64": [dummy_b64, dummy_b64],
        "use_upscale": False,
        "aspect_ratio": "16:9",
        "steps": 25
    }
    
    print("Testing generate_image API...")
    try:
        response = requests.post(url, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print("SERVER RESP:", decoded_line[:200])
                if "image_base64" in decoded_line:
                    print("Received final image! (Base64 omitted for brevity)")
                    return
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    test_api()
