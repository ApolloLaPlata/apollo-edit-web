with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
html = re.sub(r'forceDownloadAudio\([^)]+\)', 'forceDownloadAudio(${fileUrlAbs})', html)

# For the batch one, let's fix it back
html = html.replace('forceDownloadAudio(${fileUrlAbs});\\n                      logMusicMaster', 'forceDownloadAudio(url);\\n                      logMusicMaster')

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
