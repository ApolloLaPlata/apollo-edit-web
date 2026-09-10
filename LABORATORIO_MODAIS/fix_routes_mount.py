import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# The routes are currently at the bottom (after start_server)
# Let's extract them.
routes_marker = "@app.post(\"/api/music/auto_tag_lyrics\")"
if routes_marker in code:
    # Everything from @app.post("/api/music/auto_tag_lyrics") down to the end of generate_batch_ideas
    # I'll just use regex to grab the whole block
    import re
    match = re.search(r'(@app\.post\("/api/music/auto_tag_lyrics"\).*?return \{"success": False, "error": str\(e\)\})', code, re.DOTALL)
    if match:
        routes_block = match.group(1)
        
        # Remove it from the original code
        code = code.replace(routes_block, "")
        
        # Now find the app.mount("/")
        mount_str = 'app.mount("/", StaticFiles(directory=WEB_UI_DIR), name="static")'
        
        # Insert the routes block right before the mount string
        new_code = code.replace(mount_str, routes_block + "\n\n" + mount_str)
        
        with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
            f.write(new_code)
        print("Moved successfully above app.mount!")
    else:
        print("Regex match failed.")
else:
    print("Routes marker not found.")
