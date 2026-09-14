import glob

files = ["public/modal_ai_studio.html", "frontend/modal_ai_studio.html", "web_ui/modal_ai_studio.html", "modal_ai_studio.html"]

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            
        bad_str = "`${result.file_url}${result.file_url}`"
        good_str = "result.file_url"
        
        if bad_str in text:
            text = text.replace(bad_str, good_str)
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Fixed typo in {file}")
    except Exception as e:
        print(f"Error processing {file}: {e}")
