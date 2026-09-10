import re
import shutil

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/stable_audio_engine.py"
shutil.copy(file_path, file_path + ".bak")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Trocar inpaint por cond normal
content = content.replace("from stable_audio_tools.inference.generation import generate_diffusion_cond_inpaint", "from stable_audio_tools.inference.generation import generate_diffusion_cond")

# Remove hardcoded steps e cfg, muda parametros da func
pattern_params = re.compile(r"def generate_audio\(self, prompt: str, duration_s: float = 120\.0, num_inference_steps: int = 8, seed: int = 0\):")
replacement_params = r"def generate_audio(self, prompt: str, duration_s: float = 120.0, num_inference_steps: int = 100, seed: int = 0):"
content = pattern_params.sub(replacement_params, content)

# Remove steps e cfg fixos
content = re.sub(r"        steps = 8 # HARDCODED para destilado\n", "        steps = 100\n", content)
content = re.sub(r"        cfg = 1\.0 # HARDCODED para destilado\n", "        cfg = 7.0\n", content)

# Remove o inpaint call e coloca o call correto
old_call = """            output = generate_diffusion_cond_inpaint(
                self.model,
                steps=steps,
                cfg_scale=cfg,
                conditioning=conditioning,
                sample_size=self.sample_size, 
                sampler_type="pingpong",
                device="cuda"
            )"""

new_call = """            output = generate_diffusion_cond(
                self.model,
                steps=steps,
                cfg_scale=cfg,
                conditioning=conditioning,
                sample_size=self.sample_size, 
                sigma_min=0.3,
                sigma_max=500,
                sampler_type="dpmpp-3m-sde",
                device="cuda"
            )"""

if old_call in content:
    content = content.replace(old_call, new_call)
else:
    print("WARNING: Old call not found, replacing via regex")
    content = re.sub(r"generate_diffusion_cond_inpaint\([\s\S]*?device=\"cuda\"\n\s+\)", new_call, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("stable_audio_engine.py patched back to perfect!")
