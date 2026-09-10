with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Strip out the added routes from the bottom
marker = "# ROTAS INTELIGENTES PARA MÚSICA (LLM)"
if marker in code:
    parts = code.split("# =====================================================================")
    
    # We find the part containing the routes
    clean_parts = []
    routes_part = ""
    for p in parts:
        if marker in p:
            routes_part = p
        else:
            clean_parts.append(p)
            
    # Now we insert the routes_part right before def start_server
    code = "# =====================================================================".join(clean_parts)
    code = code.replace("def start_server", "# =====================================================================" + routes_part + "\ndef start_server")

    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed routes location.")
