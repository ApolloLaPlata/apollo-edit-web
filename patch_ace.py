import os

with open("backend/cloud_tools/engines/ace_step_15_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace config.guidance_scale
text = text.replace("config.guidance_scale = 7.0", "config.guidance_scale = 4.5")
text = text.replace("config.omega_scale = 7.0", "config.omega_scale = 4.5")

# Ensure steps in generate() default to 50
text = text.replace("steps: int = 64", "steps: int = 50")

with open("backend/cloud_tools/engines/ace_step_15_engine.py", "w", encoding="utf-8") as f:
    f.write(text)
print("ACE-STEP PATCHED to 4.5 CFG and 50 STEPS")
