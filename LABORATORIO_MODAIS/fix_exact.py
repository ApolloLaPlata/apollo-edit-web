with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

# exact replace for preview.innerHTML
exact_str1 = '''preview.innerHTML = 
                <div style="padding: 20px;">'''
exact_rep1 = '''preview.innerHTML = 
                <div style="padding: 20px;">'''

# exact replace for end of preview.innerHTML
exact_str2 = '''</div>
            ;'''
exact_rep2 = '''</div>
            ;'''

# exact replace for trackHtml
exact_str3 = '''const trackHtml = 
                            <div style="background: #1e1e28; padding: 15px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 15px;">'''
exact_rep3 = '''const trackHtml = 
                            <div style="background: #1e1e28; padding: 15px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 15px;">'''

# exact replace for end of trackHtml
exact_str4 = '''</a>
                            </div>
                        ;'''
exact_rep4 = '''</a>
                            </div>
                        ;'''

code = code.replace(exact_str1, exact_rep1)
code = code.replace(exact_str2, exact_rep2)
code = code.replace(exact_str3, exact_rep3)
code = code.replace(exact_str4, exact_rep4)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(code)
