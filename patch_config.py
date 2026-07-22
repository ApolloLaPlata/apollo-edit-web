import re

with open('config.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Add Gemini Key Input
gemini_ui = '''
                  <div class="form-group">
                      <label>Chave Gemini API (Motor Principal)</label>
                      <input type="password" id="key-gemini" placeholder="AIzaSy...">
                      <div class="form-help">Essencial para rodar o Apollo Copilot e o Job Engine.</div>
                  </div>
'''
c = re.sub(r'(<h3.*?Cofre de Chaves.*?</h3>)', r'\1' + gemini_ui, c)

# Add Gemini Key Loading
gemini_load = '''
              // Load Gemini
              try {
                  const apikeys = JSON.parse(localStorage.getItem('laplata_apikeys') || '[]');
                  if (apikeys.length > 0) {
                      document.getElementById('key-gemini').value = apikeys[0].key;
                  }
              } catch(e) {}
              
'''
c = re.sub(r'(const openRouterKey = localStorage.getItem\(\'apollo_openrouter_key\'\);)', gemini_load + r'\1', c)

# Add Gemini Key Saving
gemini_save = '''
              // Save Gemini
              const gemKey = document.getElementById('key-gemini').value;
              if (gemKey) {
                  const arr = [{ key: gemKey, name: 'Main Key', isActive: true, isRateLimited: false, rateLimitedUntil: 0, usageCount: 0, usageLimit: 1500, errorCount: 0, lastReset: Date.now() }];
                  localStorage.setItem('laplata_apikeys', JSON.stringify(arr));
              } else {
                  localStorage.removeItem('laplata_apikeys');
              }
              
'''
c = re.sub(r'(const orKey = document.getElementById\(\'key-openrouter\'\)\.value;)', gemini_save + r'\1', c)

with open('config.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Sweep 15 UI patch applied.')
