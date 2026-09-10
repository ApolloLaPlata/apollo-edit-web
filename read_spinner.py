with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()
    idx = text.find('function showSpinner')
    print(text[idx:idx+800])
