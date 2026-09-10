# coding: utf-8
import datetime
path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md'
with open(path, 'a', encoding='utf-8') as f:
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    f.write(f"\n\n**{date_str} (Infraestrutura Qwen e Otimizacao do Flow)**\n")
    f.write("- **Memoria Fotografica (Cache):** Adicionado hash local (vision_cache.json) na Oracle VPS para pular a requisicao do Florence-2 caso a mesma imagem seja reutilizada.\n")
    f.write("- **Smart Padding:** Alterado metodo de colagem de imagens no routes_studio.py de 'Smart Crop' (destrutivo) para 'Padding Seguro' (preserva proporcoes originais sem cortar silhuetas ou detalhes de reference sheets).\n")
    f.write("- **Gestao de Escala Modal:** Injetado asyncio.Semaphore(2) no Proxy para limitar conexoes simultaneas e evitar estouro de orcamento por cold starts/bugs.\n")
    f.write("- **Negative Prompt & Dorama Sheets:** Prompt do Nemotron foi reescrito para distinguir Turnarounds de 1 personagem vs. Character Sheets de multiplos personagens (Doramas). Se detectado multiplos, o LLM remove 'SINGLE CHARACTER ONLY' e usa restricoes de separacao para evitar clonagem/fusao, e forca acao dinamica para evitar copia identica da pose. Tambem foi incluida geracao automatica de Negative Prompts baseados no estilo visual.\n")
    f.write("- **Snapshot Modal:** Injetado o boot do subprocesso ComfyUI para dentro da fase de build da memoria (@modal.enter()) na Modal, permitindo um carregamento praticamente instantaneo de imagens/videos via Qwen.\n")
