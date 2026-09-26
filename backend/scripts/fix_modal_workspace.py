import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Change the endpoints mapping to use an environment variable or default to apollolaplata
old_mapping = """        endpoints = {
            "Qwen-TTS": "https://apollolaplata--apollo-api-qwen-tts.modal.run",
            "XTTS": "https://apollolaplata--apollo-api-xtts.modal.run",
            "Moss-TTS": "https://apollolaplata--apollo-api-moss-tts.modal.run",
            "F5-TTS": "https://apollolaplata--apollo-api-f5-tts.modal.run",
            "Fish-Speech": "https://apollolaplata--apollo-api-fish-tts.modal.run",
            "Melo-TTS": "https://apollolaplata--apollo-api-melo-tts.modal.run",
            "ChatTTS": "https://apollolaplata--apollo-api-chattts.modal.run",
            "CosyVoice": "https://apollolaplata--apollo-api-cosyvoice.modal.run",
            "OpenVoice": "https://apollolaplata--apollo-api-openvoice.modal.run"
        }"""

new_mapping = """        import os
        workspace = os.getenv("MODAL_WORKSPACE_TTS", "apollolaplata")
        endpoints = {
            "Qwen-TTS": f"https://{workspace}--apollo-api-qwen-tts.modal.run",
            "XTTS": f"https://{workspace}--apollo-api-xtts.modal.run",
            "Moss-TTS": f"https://{workspace}--apollo-api-moss-tts.modal.run",
            "F5-TTS": f"https://{workspace}--apollo-api-f5-tts.modal.run",
            "Fish-Speech": f"https://{workspace}--apollo-api-fish-tts.modal.run",
            "Melo-TTS": f"https://{workspace}--apollo-api-melo-tts.modal.run",
            "ChatTTS": f"https://{workspace}--apollo-api-chattts.modal.run",
            "CosyVoice": f"https://{workspace}--apollo-api-cosyvoice.modal.run",
            "OpenVoice": f"https://{workspace}--apollo-api-openvoice.modal.run"
        }"""

content = content.replace(old_mapping, new_mapping)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("routes_studio.py updated to support dynamic workspace!")
