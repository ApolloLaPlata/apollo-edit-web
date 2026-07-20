import os

patch_code = """
import customtkinter as ctk

class CTkLabelFrame(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, corner_radius=10, fg_color="#232329", **kwargs)
        if text:
            self.lbl = ctk.CTkLabel(self, text=text, font=("Segoe UI", 13, "bold"), text_color="#0A84FF")
            self.lbl.pack(anchor="w", padx=10, pady=(5, 0))

ctk.CTkLabelFrame = CTkLabelFrame
"""

for filename in ['aba_dashboard.py', 'aba_mapeador_automatico.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class CTkLabelFrame' not in content:
        content = content.replace('import customtkinter as ctk', patch_code, 1)
        content = content.replace('ctk.CTkLabelFrame', 'ctk.CTkLabelFrame')
        content = content.replace('ctk.CTkFrame(parent, text=', 'ctk.CTkLabelFrame(parent, text=')
        content = content.replace('ctk.CTkFrame(self, text=', 'ctk.CTkLabelFrame(self, text=')
        content = content.replace('ctk.CTkFrame(mid_frame, text=', 'ctk.CTkLabelFrame(mid_frame, text=')
        content = content.replace('ctk.CTkFrame(left_frame, text=', 'ctk.CTkLabelFrame(left_frame, text=')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

print("Patch applied successfully.")
