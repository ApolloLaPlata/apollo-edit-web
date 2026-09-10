import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# The routes block starts at '# ROTAS INTELIGENTES PARA MÚSICA (LLM)'
# and goes to the end of the file.
parts = code.split("# ROTAS INTELIGENTES PARA MÚSICA (LLM)")
if len(parts) > 1:
    clean_top = parts[0]
    routes = "# ROTAS INTELIGENTES PARA MÚSICA (LLM)" + parts[1]
    
    # We want to remove the routes from the bottom
    # Where does if __name__ == "__main__": start?
    main_split = clean_top.split('if __name__ == "__main__":')
    if len(main_split) == 2:
        new_code = main_split[0] + "\n" + routes + "\n\nif __name__ == \"__main__\":\n" + main_split[1]
        # Clean up any duplicated or hanging routes at the end just in case
        new_code = new_code.replace("# ROTAS INTELIGENTES PARA MÚSICA (LLM)\n# =====================================================================\n\n@app.post", "")
        
        with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
            f.write(new_code)
        print("Moved successfully!")
    else:
        print("Could not find __main__")
else:
    print("Could not find routes marker.")
