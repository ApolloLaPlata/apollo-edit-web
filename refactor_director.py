import os
import re

file_path = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\aba_mapeador_automatico.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace class definition and inheritance
content = content.replace("class AbaMapeadorAutomatico(ctk.CTkFrame):", "import customtkinter as ctk\n\nclass AbaMapeadorAutomatico(ctk.CTkFrame):")
content = content.replace("super().__init__(parent)", "super().__init__(parent, fg_color=\"transparent\")")

# Replace generic widgets
content = content.replace("ctk.CTkFrame", "ctk.CTkFrame")
content = content.replace("ctk.CTkLabel", "ctk.CTkLabel")
content = content.replace("ctk.CTkLabel", "ctk.CTkLabel")
content = content.replace("ctk.CTkButton", "ctk.CTkButton")
content = content.replace("ctk.CTkEntry", "ctk.CTkEntry")
content = content.replace("ctk.CTkEntry", "ctk.CTkEntry")
content = content.replace("ctk.CTkSwitch", "ctk.CTkSwitch")
content = content.replace("ctk.CTkSwitch", "ctk.CTkSwitch")
content = content.replace("ttk.Radiobutton", "ctk.CTkRadioButton")
content = content.replace("ctk.CTkOptionMenu", "ctk.CTkOptionMenu")

# LabelFrames can just be CTkFrames, we'll lose the physical box text but we can style them
content = content.replace('ctk.CTkLabelFrame', 'ctk.CTkFrame')

# Handle state assignments
content = content.replace("state='readonly'", "state='normal'") # OptionMenu handles read-only naturally
content = content.replace('state="readonly"', 'state="normal"')

# Replace bd, relief, and standard styling attributes that CTk doesn't like
content = re.sub(r',\s*bd=\d+', '', content)
content = re.sub(r',\s*relief=tk\.[A-Z]+', '', content)
content = re.sub(r',\s*relief="[a-z]+"', '', content)

# PanedWindow doesn't exist in CTk, we can just use a normal frame and pack side by side
content = content.replace("ttk.PanedWindow(self, orient=tk.HORIZONTAL)", "ctk.CTkFrame(self, fg_color=\"transparent\")")
content = content.replace("main_pane.add(left_container, weight=3)", "left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)")
content = content.replace("main_pane.add(right_frame, weight=2)", "right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)")

# Configure method replacement
content = content.replace('.config(text=', '.configure(text=')
content = content.replace('.config(state=', '.configure(state=')
content = content.replace('.config(values=', '.configure(values=')

# We leave tk.Listbox and tk.Canvas alone because they are complex and can just be styled dark.
content = content.replace("bg='white'", "bg='#232329'")
content = content.replace('bg="white"', 'bg="#232329"')

with open('E:\\MEUS PROGRAMAS\\APOLLO_STUDIO\\aba_mapeador_automatico.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Director refactor base applied.")
