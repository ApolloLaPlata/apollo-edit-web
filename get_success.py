import re
with open("public/modal_ai_studio.html", "r", encoding="utf-8") as f:
    text = f.read()

match = re.search(r'let result = initResult;.*?if \(result\.success\)', text, re.DOTALL)
if match:
    # Print the lines right after result.success
    success_block = text[match.end():match.end()+2000]
    print(success_block)
