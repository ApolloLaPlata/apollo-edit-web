import sys
sys.path.append('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB')

channel = 'default'
try:
    from backend.cloud_tools.engines.xtts_engine import XttsEngine
    import os
    import httpx
    
    xtts = XttsEngine()
    print('XTTS init OK')
    
    from config_manager import ConfigManager
    cm = ConfigManager(os.path.join('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB', 'admin_config.json'))
    channel_cfg = cm.get(channel, {})
    contexto = channel_cfg.get('channel_context', '')
    print('Config OK')
    
    ref_bytes = b''
    if os.path.exists('default_voice.wav'):
        with open('default_voice.wav', 'rb') as f:
            ref_bytes = f.read()
    elif os.path.exists('web_ui/assets/peter_parker.wav'):
        with open('web_ui/assets/peter_parker.wav', 'rb') as f:
            ref_bytes = f.read()
    print('Ref Bytes:', len(ref_bytes))
    
except Exception as e:
    import traceback
    print(traceback.format_exc())
