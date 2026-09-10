with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'async def audio_interceptor():' in line:
        start_idx = i
    if start_idx != -1 and 'return StreamingResponse(audio_interceptor())' in line and i > start_idx:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    indent = "            "
    new_interceptor = [
        indent + "async def audio_interceptor():\n",
        indent + "    yield json.dumps({\"status\": \"processing\", \"message\": \"Iniciando geração de áudio no Modal...\"}).encode('utf-8') + b'\\n'\n",
        indent + "    try:\n",
        indent + "        print(f\"[Modal Proxy] Interceptando requisição para audio_lab...\")\n",
        indent + "        import httpx\n",
        indent + "        import asyncio\n",
        indent + "        async with httpx.AsyncClient(timeout=1200.0) as local_client:\n",
        indent + "            task = asyncio.create_task(local_client.post(modal_url, content=body, headers=req_headers))\n",
        indent + "            \n",
        indent + "            while not task.done():\n",
        indent + "                yield json.dumps({\"status\": \"processing\", \"message\": \"Processando áudio na nuvem...\"}).encode('utf-8') + b'\\n'\n",
        indent + "                await asyncio.sleep(5)\n",
        indent + "                \n",
        indent + "            response = task.result()\n",
        indent + "            \n",
        indent + "            if response.status_code != 200:\n",
        indent + "                yield response.content\n",
        indent + "                return\n",
        indent + "            \n",
        indent + "            data = response.json()\n",
        indent + "            if data.get(\"status\") == \"success\" and \"audio_base64\" in data:\n",
        indent + "                import base64\n",
        indent + "                b64_string = data[\"audio_base64\"]\n",
        indent + "                audio_bytes = base64.b64decode(b64_string)\n",
        indent + "                \n",
        indent + "                filename = f\"audio_{uuid.uuid4().hex}.wav\"\n",
        indent + "                filepath = f\"/home/ubuntu/apollo_edit/media/{filename}\"\n",
        indent + "                with open(filepath, \"wb\") as af:\n",
        indent + "                    af.write(audio_bytes)\n",
        indent + "                \n",
        indent + "                print(f\"[Modal Proxy] Audio salvo na Oracle: {filename}\")\n",
        indent + "                data.pop(\"audio_base64\", None)\n",
        indent + "                data[\"audio_url\"] = f\"https://www.apolloedit.com.br/media/{filename}\"\n",
        indent + "                data[\"message\"] = \"Audio gerado e salvo com sucesso!\"\n",
        indent + "                \n",
        indent + "                yield json.dumps(data).encode('utf-8') + b'\\n'\n",
        indent + "            else:\n",
        indent + "                yield response.content + b'\\n'\n",
        indent + "    except Exception as e:\n",
        indent + "        print(f\"[Modal Proxy Audio Error]: {e}\")\n",
        indent + "        yield json.dumps({\"status\": \"error\", \"message\": f\"Erro proxy interceptor: {str(e)}\"}).encode('utf-8') + b'\\n'\n",
        "\n"
    ]
    lines = lines[:start_idx] + new_interceptor + lines[end_idx:]

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
try:
    py_compile.compile('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web_downloaded.py', doraise=True)
    print("Sintaxe Python Correta!")
except Exception as e:
    print(f"Erro de sintaxe: {e}")
