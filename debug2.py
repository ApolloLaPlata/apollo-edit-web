with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('batchTracksList')
print(repr(content[idx:idx+250].encode('utf-8')))

idx = content.find('batchTracksList', idx+1)
print(repr(content[idx:idx+250].encode('utf-8')))
