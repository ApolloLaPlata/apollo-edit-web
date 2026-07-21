import re
html = open('admin.html', encoding='utf-8').read()
js = open('admin.js', encoding='utf-8').read()
ids_html = re.findall(r'id=["\']([a-zA-Z0-9_-]+)["\']', html)
ids_js = re.findall(r'getElementById\([\'"]([a-zA-Z0-9_-]+)[\'"]\)', js)
missing = [i for i in ids_js if i not in ids_html]
print('Missing IDs in HTML:', set(missing))
