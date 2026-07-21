import os
import re
import codecs
import glob

html_files = glob.glob(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\*.html')

core_scripts = [
    'laplata_db.js',
    'laplata_settings.js',
    'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2',
    'auth.js',
    'apollo_sfx.js',
    'apollo_notifications.js',
    'transfer_hud.js',
    'copilot_hud.js',
    'apollo_assistant.js'
]

# We want to ensure all these are present.
injection_block = """
    <!-- APOLLO OS CORE (Auto-Injected) -->
    <script src="laplata_db.js"></script>
    <script src="laplata_settings.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script src="auth.js"></script>
    <script src="apollo_sfx.js"></script>
    <script src="apollo_notifications.js"></script>
    <script src="transfer_hud.js"></script>
    <script src="copilot_hud.js"></script>
    <script src="apollo_assistant.js"></script>
</body>"""

count = 0

for filepath in html_files:
    try:
        with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if apollo_assistant.js is already there
        if 'apollo_assistant.js' not in content or 'transfer_hud.js' not in content:
            # We will clean up any existing duplicate tags to avoid conflicts
            for script in core_scripts:
                # remove lines that contain this script to avoid double loading
                pattern = r'<script\s+[^>]*src=[\'"]' + re.escape(script) + r'[\'"][^>]*>\s*</script>\s*'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)

            # Now inject the clean block right before </body>
            if '</body>' in content:
                content = content.replace('</body>', injection_block)
            else:
                # If no </body>, append to end
                content += injection_block.replace('</body>', '')
            
            with codecs.open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            count += 1
            print(f"Injected into {os.path.basename(filepath)}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(f"\nSuccessfully injected OS Core into {count} files.")
