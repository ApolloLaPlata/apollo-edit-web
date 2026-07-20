import glob
import re
import os

files = glob.glob('E:/MEUS PROGRAMAS/APOLLO_STUDIO/*.py')
with open('E:/MEUS PROGRAMAS/APOLLO_STUDIO/state_usages.txt', 'w', encoding='utf-8') as out:
    for f in files:
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if 'state=' in line and 'ctk.' in line:
                    out.write(f"{os.path.basename(f)}:{i+1}: {line.strip()}\n")
                elif 'state=' in line and '.configure(' in line:
                    out.write(f"{os.path.basename(f)}:{i+1}: {line.strip()}\n")
