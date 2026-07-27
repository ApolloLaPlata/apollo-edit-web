import sys

def restore_force_cpu(gold_file, target_file):
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_content = f.read()
    
    start_str = "@contextmanager\ndef force_cpu_during_snapshot():"
    end_str = "\n@app.cls("
    
    start_idx = gold_content.find(start_str)
    end_idx = gold_content.find(end_str, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print(f"Could not find block in {gold_file}")
        sys.exit(1)
        
    gold_block = gold_content[start_idx:end_idx]
    
    with open(target_file, 'r', encoding='utf-8') as f:
        target_content = f.read()
        
    t_start_idx = target_content.find(start_str)
    t_end_idx = target_content.find(end_str, t_start_idx)
    
    if t_start_idx == -1 or t_end_idx == -1:
        print(f"Could not find block in {target_file}")
        sys.exit(1)
        
    new_content = target_content[:t_start_idx] + gold_block + target_content[t_end_idx:]
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully replaced in {target_file}")

restore_force_cpu(r'backend\cloud_tools\copia_seguranca_ouro\universal_engine.py', r'backend\cloud_tools\engines\universal_engine.py')
restore_force_cpu(r'backend\cloud_tools\copia_seguranca_ouro\flux_engine.py', r'backend\cloud_tools\engines\flux_engine.py')
restore_force_cpu(r'backend\cloud_tools\copia_seguranca_ouro\flux_txt2img_engine.py', r'backend\cloud_tools\engines\flux_txt2img_engine.py')
