import json
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'r') as f:
    data = json.load(f)

for rw in data.get('rewrites', []):
    if rw.get('source') == '/media/(.*)':
        rw['destination'] = 'http://163.176.135.59/media/'

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'w') as f:
    json.dump(data, f, indent=4)
