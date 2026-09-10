with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'if path == "generate/audio_lab":' in line:
        start_idx = i
    if start_idx != -1 and 'return StreamingResponse(audio_interceptor())' in line and i > start_idx:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_interceptor = [
        "        if path == \"generate/audio_lab\":\n",
        "            import json\n",
        "            import uuid\n",
        "            \n",
        "            async def audio_interceptor():\n",
        "                yield json.dumps({\"status\": \"processing\", \"message\": \"Iniciando geração de áudio no Modal...\"}).encode('utf-8') + b'\\n'\n",
        "                try:\n",
        "                    print(f\"[Modal Proxy] Interceptando requisição para audio_lab...\")\n",
        "                    import httpx\n",
        "                    import asyncio\n",
        "                    async with httpx.AsyncClient(timeout=1200.0) as local_client:\n",
        "                        task = asyncio.create_task(local_client.post(modal_url, content=body, headers=req_headers))\n",
        "                        \n",
        "                        while not task.done():\n",
        "                            yield json.dumps({\"status\": \"processing\", \"message\": \"Processando áudio na nuvem...\"}).encode('utf-8') + b'\\n'\n",
        "                            await asyncio.sleep(5)\n",
        "                            \n",
        "                        response = task.result()\n",
        "                        \n",
        "                        if response.status_code != 200:\n",
        "                            yield response.content\n",
        "                            return\n",
        "                        \n",
        "                        data = response.json()\n",
        "                        if data.get(\"status\") == \"success\" and \"audio_base64\" in data:\n",
        "                            import base64\n",
        "                            b64_string = data[\"audio_base64\"]\n",
        "                            audio_bytes = base64.b64decode(b64_string)\n",
        "                            \n",
        "                            filename = f\"audio_{uuid.uuid4().hex}.wav\"\n",
        "                            filepath = f\"/home/ubuntu/apollo_edit/media/{filename}\"\n",
        "                            with open(filepath, \"wb\") as af:\n",
        "                                af.write(audio_bytes)\n",
        "                            \n",
        "                            print(f\"[Modal Proxy] Audio salvo na Oracle: {filename}\")\n",
        "                            data.pop(\"audio_base64\", None)\n",
        "                            data[\"audio_url\"] = f\"https://www.apolloedit.com.br/media/{filename}\"\n",
        "                            data[\"message\"] = \"Audio gerado e salvo com sucesso!\"\n",
        "                            \n",
        "                            yield json.dumps(data).encode('utf-8') + b'\\n'\n",
        "                        else:\n",
        "                            yield response.content + b'\\n'\n",
        "                except Exception as e:\n",
        "                    print(f\"[Modal Proxy Audio Error]: {e}\")\n",
        "                    yield json.dumps({\"status\": \"error\", \"message\": f\"Erro proxy interceptor: {str(e)}\"}).encode('utf-8') + b'\\n'\n",
        "\n",
        "            return StreamingResponse(audio_interceptor())\n"
    ]
    lines = lines[:start_idx] + new_interceptor + lines[end_idx+1:]

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
try:
    py_compile.compile('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded_2.py', doraise=True)
    print("Sintaxe Python Correta!")
except Exception as e:
    print(f"Erro de sintaxe: {e}")
