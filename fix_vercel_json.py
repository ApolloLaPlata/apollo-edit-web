import sys
import json

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

has_media = any(r.get('source') == '/media/(.*)' for r in config.get('rewrites', []))
if not has_media:
    config['rewrites'].insert(0, {
        "source": "/media/(.*)",
        "destination": "http://163.176.135.59/media/"
    })
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
