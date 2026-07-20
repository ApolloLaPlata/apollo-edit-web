import json
import os

base_workflow_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/texto_flux2/image_flux2_text_to_image.json"
out_workflow_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2_pulid_dynamic.json"

with open(base_workflow_path, "r", encoding="utf-8") as f:
    workflow = json.load(f)

# Find the UNETLoader (which outputs the base FLUX model)
unet_node_id = None
sampler_node_id = None
for nid, node in workflow.items():
    if node.get("class_type") == "UNETLoader":
        unet_node_id = nid
    if node.get("class_type") in ["KSampler", "SamplerCustomAdvanced"]:
        sampler_node_id = nid

print(f"Found UNETLoader: {unet_node_id}")
print(f"Found Sampler: {sampler_node_id}")

# Find which node is feeding 'model' into BasicGuider
basic_guider_id = None
for nid, node in workflow.items():
    if node.get("class_type") == "BasicGuider":
        basic_guider_id = nid

print(f"Found UNETLoader: {unet_node_id}")
print(f"Found BasicGuider: {basic_guider_id}")

basic_guider_node = workflow[basic_guider_id]
original_model_link = basic_guider_node["inputs"]["model"]

# Add PuLID Nodes
pulid_model_id = "1001"
insightface_id = "1002"
evaclip_id = "1003"
apply_pulid_id = "1004"
apollo_image_id = "1005"

workflow[pulid_model_id] = {
    "class_type": "PulidFluxModelLoader",
    "inputs": {
        "pulid_file": "pulid_flux_v0.9.0.safetensors"
    }
}

workflow[insightface_id] = {
    "class_type": "PulidFluxInsightFaceLoader",
    "inputs": {
        "provider": "CUDA"
    }
}

workflow[evaclip_id] = {
    "class_type": "PulidFluxEvaClipLoader",
    "inputs": {}
}

# Add APOLLO_INPUT_IMAGE placeholder
workflow[apollo_image_id] = {
    "class_type": "LoadImage",
    "inputs": {
        "image": "apollo_universal_input.png"
    },
    "_meta": {
        "title": "APOLLO_INPUT_IMAGE"
    }
}

# Apply PuLID Node
workflow[apply_pulid_id] = {
    "class_type": "ApplyPulidFlux",
    "inputs": {
        "model": original_model_link,
        "pulid_flux": [pulid_model_id, 0],
        "eva_clip": [evaclip_id, 0],
        "face_analysis": [insightface_id, 0],
        "image": [apollo_image_id, 0],
        "weight": 1.0,
        "start_at": 0.0,
        "end_at": 1.0
    }
}

# Redirect BasicGuider to use Apply PuLID output
basic_guider_node["inputs"]["model"] = [apply_pulid_id, 0]

with open(out_workflow_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=4)

print(f"Successfully generated {out_workflow_path}")
