import sys
import asyncio
from backend.cloud_tools.apollo_modal_engine import api_generate_tts

class DummyReq:
    engine = 'moss'
    text = 'Hello world, this is a test of the Moss TTS system'
    ref_text = ''
    reference_audio_base64 = ''
    language = ''

req = DummyReq()
res = api_generate_tts(req)
import json
async def test():
    async for chunk in res.body_iterator:
        print(chunk)
asyncio.run(test())
