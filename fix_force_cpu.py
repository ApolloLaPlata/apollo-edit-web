import re

def extract_force_cpu(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'(@contextmanager\ndef force_cpu_during_snapshot\(\):.*?)(?=\n@app\.cls|\ndef )', content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def replace_force_cpu(filepath, new_code):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = re.sub(r'(@contextmanager\ndef force_cpu_during_snapshot\(\):.*?)(?=\n@app\.cls|\ndef )', new_code, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

gold_path = r'backend\cloud_tools\copia_seguranca_ouro\universal_engine.py'
gold_code = extract_force_cpu(gold_path)

if gold_code:
    print('Found gold code, length:', len(gold_code))
    replace_force_cpu(r'backend\cloud_tools\engines\universal_engine.py', gold_code)
    replace_force_cpu(r'backend\cloud_tools\engines\flux_engine.py', gold_code)
    replace_force_cpu(r'backend\cloud_tools\engines\flux_txt2img_engine.py', gold_code)
    print('Successfully restored force_cpu_during_snapshot in all engines.')
else:
    print('Failed to extract gold code.')
