filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\news_logic.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# We need to inject webhook call after the deepdive result is rendered
# The exact text after the resDiv.innerHTML assignment inside the success block ends with:
#             }
#         } else {
old_block = "            if (resDiv) {\n"  # first part
# better: look for the unique finally block in newsDeepDive
target = "        } else {\n            throw new Error(data.error || 'Erro desconhecido');\n        }\n    } catch (err) {\n        if (resDiv) {\n            resDiv.innerHTML = `<div style=\"color: red; font-size: 12px;\">Erro: ${err.message}</div>`;\n        }\n    } finally {\n        if (btn) btn.innerHTML = '<i class=\"fas fa-search-plus\"></i>';\n    }\n}"

replacement = """        // Dispara Webhook se configurado
            const webhookUrl = localStorage.getItem('webhook_url_deepdive');
            if (webhookUrl && item) {
                try {
                    fetch(webhookUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: item.title,
                            summary: item.summary,
                            url: item.url,
                            deepdive_text: data.content || '',
                            timestamp: new Date().toISOString()
                        })
                    }).catch(() => {}); // fire and forget
                } catch(e) {}
            }
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (err) {
        if (resDiv) {
            resDiv.innerHTML = `<div style="color: red; font-size: 12px;">Erro: ${err.message}</div>`;
        }
    } finally {
        if (btn) btn.innerHTML = '<i class="fas fa-search-plus"></i>';
    }
}"""

if "webhook_url_deepdive" not in content:
    content = content.replace(target, replacement, 1)
    with open(filepath, 'w', encoding='latin-1') as f:
        f.write(content)
    print("Webhook injected into newsDeepDive in news_logic.js!")
else:
    print("Already patched.")
