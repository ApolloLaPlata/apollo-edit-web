import sys
from backend.cloud_tools.apollo_modal_engine import api_generate_tts

class DummyReq:
    engine = 'qwen'
    text = 'Hello world, this is a test of the Qwen TTS system.'
    ref_text = ''
    reference_audio_base64 = ''
    language = ''

req = DummyReq()
try:
    res = api_generate_tts(req)
    print('SUCCESS')
    print(res.keys() if isinstance(res, dict) else res)
except Exception as e:
    print('ERROR:', e)
