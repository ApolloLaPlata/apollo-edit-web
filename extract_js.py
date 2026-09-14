import sys, re
with open('public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    with open(f'script_{i}.js', 'w', encoding='utf-8') as out:
        out.write(s)
