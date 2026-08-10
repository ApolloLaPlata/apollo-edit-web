import os
for root, dirs, files in os.walk('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if '["timestamp"]' in line or "['timestamp']" in line:
                            print(f'{path}:{i+1}: {line.strip()}')
            except:
                pass
