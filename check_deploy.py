import urllib.request
html = urllib.request.urlopen('https://apollo-edit-gx2jfq4w5-apollo-edit-web.vercel.app/modal_ai_studio.html').read().decode('utf-8')
for line in html.split('\n'):
    if 'id="musicRefAudio"' in line:
        print(line.strip())
