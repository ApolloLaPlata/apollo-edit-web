import json
import base64

WORKFLOW_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\Mockup de Produto(Flux.2 Dev FF8)\image_flux2_fp8.json"

with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
    workflow = json.load(f)

saved_filenames = ["apollo_universal_input_0.png", "apollo_universal_input_1.png"]
nodes_updated = []
apollo_image_node_id = None

# Mock the title check
for node_id, node in list(workflow.items()):
    title = node.get("_meta", {}).get("title", "")
    if title == "APOLLO_INPUT_IMAGE":
        apollo_image_node_id = node_id

# 3. Lógica de Grafo Dinâmico (Roteamento Múltiplo Inteligente)
if saved_filenames:
    # 3.1. Procura TODOS os nós LoadImage originais no JSON
    load_image_nodes = []
    for nid, n_data in workflow.items():
        if n_data.get("class_type") == "LoadImage":
            load_image_nodes.append(nid)
    
    # Se achamos nós LoadImage, ordenamos pela chave do nó para ser determinístico
    load_image_nodes.sort(key=lambda x: str(x))
    
    # 3.2. Se a quantidade de arquivos salvos bater com a quantidade de LoadImages ou for menor, faz mapeamento 1:1
    if len(load_image_nodes) > 1 and len(saved_filenames) > 1:
        for i, filename in enumerate(saved_filenames):
            if i < len(load_image_nodes):
                target_node_id = load_image_nodes[i]
                workflow[target_node_id]["inputs"]["image"] = filename
                nodes_updated.append(f"LoadImage_1to1({target_node_id})")
    
    # 3.3. FALLBACK: Se houver apenas 1 LoadImage mas múltiplas fotos, agrupa tudo no ImageBatch como antes
    elif apollo_image_node_id: 
        original_node = workflow[apollo_image_node_id]
        final_output_node_id = None
        
        if len(saved_filenames) == 1:
            original_node["inputs"]["image"] = saved_filenames[0]
            final_output_node_id = apollo_image_node_id
            nodes_updated.append(f"APOLLO_INPUT_IMAGE_SINGLE({apollo_image_node_id})")
        else:
            batch_nodes = []
            load_nodes = []
            for i, filename in enumerate(saved_filenames):
                new_id = f"APOLLO_LOAD_{i}"
                new_node = json.loads(json.dumps(original_node))
                new_node["inputs"]["image"] = filename
                workflow[new_id] = new_node
                load_nodes.append(new_id)
            current_output = load_nodes[0]
            for i in range(1, len(load_nodes)):
                batch_id = f"APOLLO_BATCH_{i}"
                workflow[batch_id] = {
                    "class_type": "ImageBatch",
                    "inputs": {
                        "image1": [current_output, 0],
                        "image2": [load_nodes[i], 0]
                    }
                }
                current_output = batch_id
            final_output_node_id = current_output
            for nid, n_data in workflow.items():
                if nid == apollo_image_node_id or nid.startswith("APOLLO_"): continue
                for port_name, port_val in n_data.get("inputs", {}).items():
                    if isinstance(port_val, list) and port_val[0] == apollo_image_node_id:
                        workflow[nid]["inputs"][port_name][0] = final_output_node_id
                        
            del workflow[apollo_image_node_id]
            nodes_updated.append(f"APOLLO_INPUT_IMAGE_BATCH_FALLBACK({len(saved_filenames)} imgs)")

print("Nos modificados:", nodes_updated)
print("Node 42 image:", workflow.get("42", {}).get("inputs", {}).get("image"))
print("Node 46 image:", workflow.get("46", {}).get("inputs", {}).get("image"))
