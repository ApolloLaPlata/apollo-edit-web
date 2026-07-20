import os
import re

file_path = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\aba_dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace class definition and inheritance
content = content.replace("class AbaDashboard(ctk.CTkFrame):", "import customtkinter as ctk\n\nclass AbaDashboard(ctk.CTkFrame):")
content = content.replace("super().__init__(parent)", "super().__init__(parent, fg_color=\"transparent\")")

# Replace generic ttk and tk widgets
content = content.replace("ctk.CTkFrame", "ctk.CTkFrame")
content = content.replace("ctk.CTkFrame", "ctk.CTkFrame")
content = content.replace("ctk.CTkLabel", "ctk.CTkLabel")
content = content.replace("ctk.CTkLabel", "ctk.CTkLabel")
content = content.replace("ctk.CTkButton", "ctk.CTkButton")

# Update specific elements
content = content.replace('ttk.Notebook(main)', 'ctk.CTkTabview(main)')
content = content.replace('ctk.CTkLabelFrame', 'ctk.CTkFrame') # We will style it as a normal frame with inner padding
content = content.replace('bd=0', 'fg_color="transparent"')
content = content.replace('relief=tk.RIDGE', 'corner_radius=10, fg_color="#232329"')

# In custom methods, config(text=) must be configure(text=)
content = content.replace('.config(text=', '.configure(text=')

with open('E:\\MEUS PROGRAMAS\\APOLLO_STUDIO\\aba_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard refactor base applied.")
