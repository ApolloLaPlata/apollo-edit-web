import re
import os

paths = [
    r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html',
    r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
]

for html_path in paths:
    if not os.path.exists(html_path):
        continue
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(const res = await fetch\(url, \{[\s\S]*?body: JSON.stringify\(\{ prompt, image_base64: imageBase64, model, preset, aspect_ratio, duration \}\)\s*\}\);)[\s\S]*?(if \(data\.status === \'success\' && data\.video_base64\) \{)', re.MULTILINE)

    replacement = r'''\1
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(HTTP : );
        }

        const initialData = await res.json();
        let data = null;

        if (initialData.status === "processing" && initialData.job_id) {
            const jobId = initialData.job_id;
            log(?? Job enfileirado no backend (ID: ...). Iniciando polling..., 'info');
            
            let jobSuccess = false;
            while (!jobSuccess) {
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                const now = Math.floor((Date.now() - startTime)/1000);
                log(?? Consultando status... (s), 'info');
                document.getElementById('spinnerLabel').textContent = Gerando Vídeo... s;
                
                const statusRes = await fetch(/api/studio/modal/status/);
                if (!statusRes.ok) {
                    throw new Error(Erro ao consultar status: HTTP );
                }
                const statusData = await statusRes.json();
                
                if (statusData.status === 'success') {
                    jobSuccess = true;
                    if (typeof statusData.content === 'string') {
                        data = JSON.parse(statusData.content);
                    } else {
                        data = statusData.content;
                    }
                } else if (statusData.status === 'error') {
                    throw new Error(statusData.message || 'Erro na nuvem ao processar vídeo.');
                }
            }
        } else {
            data = initialData;
        }

        \2'''

    new_content = re.sub(pattern, replacement, content)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Modificado {html_path}!')

