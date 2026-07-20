import json
import os
import glob
from ai_director_pipeline import AIDirectorPipeline

class AIEditorCopilot:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.pipeline = AIDirectorPipeline(config_manager) if config_manager else None

    def _discover_local_media(self):
        """Busca mídias disponíveis nas pastas configuradas (overlay_dirs) e na pasta raiz do projeto."""
        media_files = []
        dirs_to_check = ['Midias', 'B-Rolls', 'Assets']
        
        if self.config_manager:
            estetica = self.config_manager.get("estetica_canal", {})
            overlay_dirs = estetica.get("overlay_dirs", [])
            sfx_dir = estetica.get("sfx_dir", "")
            
            if overlay_dirs:
                dirs_to_check.extend(overlay_dirs)
            if sfx_dir and os.path.exists(sfx_dir):
                dirs_to_check.append(sfx_dir)
            
        # Pega o diretório do projeto (assumindo que estamos dentro da raiz)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for d in set(dirs_to_check):
            abs_dir = os.path.join(base_dir, d) if not os.path.isabs(d) else d
            if os.path.isdir(abs_dir):
                # Busca recursivamente alguns formatos comuns
                for ext in ('*.mp4', '*.mov', '*.png', '*.jpg', '*.webp', '*.mp3', '*.wav'):
                    for file_path in glob.glob(os.path.join(abs_dir, '**', ext), recursive=True):
                        # Retornar caminho relativo para não expor o PC inteiro à IA, mas absoluto funciona também
                        # Aqui enviaremos os nomes dos arquivos para a IA saber o que tem.
                        media_files.append({
                            "name": os.path.basename(file_path),
                            "path": file_path.replace('\\', '/')
                        })
        return media_files

    def process_chat(self, user_message, timeline_state, chat_history=None):
        """
        Processa uma mensagem de chat vinda da Timeline Web.
        Retorna um dicionário contendo:
        {
           "message": "Resposta em texto para o usuário",
           "operations": [ { "type": "add_clip", ... } ]
        }
        """
        if not self.pipeline or not self.pipeline.is_active():
            return {
                "message": "⚠️ O Copiloto IA está desativado. Configure uma chave de API (Gemini/OpenAI) nas configurações globais.",
                "operations": []
            }

        available_media = self._discover_local_media()
        
        # Constrói o contexto da timeline de forma simplificada
        simplified_timeline = []
        for clip in timeline_state.get('clips', []):
            simplified_timeline.append({
                "id": clip.get("id"),
                "type": clip.get("type"),
                "name": clip.get("name"),
                "track": clip.get("track"),
                "start": clip.get("start"),
                "duration": clip.get("duration"),
                "scale": clip.get("scale"),
                "x": clip.get("x"),
                "y": clip.get("y")
            })

        system_prompt = f"""Você é o Copiloto IA do Apollo Web Editor, um especialista em edição de vídeo.
Seu objetivo é ajudar o usuário a editar a timeline respondendo às suas mensagens e, quando solicitado, modificando a timeline através de operações JSON.

=== ESTADO ATUAL DA TIMELINE ===
Clipes: {json.dumps(simplified_timeline, indent=2, ensure_ascii=False)}
(Tempo atual da agulha: {timeline_state.get('currentTime', 0)}s)

=== MÍDIAS LOCAIS DISPONÍVEIS ===
Você tem acesso aos seguintes arquivos no computador do usuário para usar em b-rolls, overlays ou áudios:
{json.dumps(available_media[:50], indent=2, ensure_ascii=False)}
(Limitado aos primeiros 50 arquivos para referência)

=== REGRAS DE RETORNO ===
Você DEVE retornar APENAS UM JSON VÁLIDO contendo:
1. "message": O que você dirá ao usuário no chat (em português).
2. "operations": Uma lista de operações a aplicar na timeline. Deixe vazio se for apenas conversa.

DICA SFX: Se o usuário pedir "botar efeito sonoro" ou "gerar efeito sonoro", busque os arquivos de áudio (.mp3, .wav) na lista de mídias disponíveis que se encaixem no contexto e adicione usando track "a1" ou "a2" e clip_type "audio".

Tipos de operação suportados:
- {{"type": "add_clip", "track": "v1"|"v2"|"a1"|"a2", "start": float, "duration": float, "path": "caminho_do_arquivo", "clip_type": "video"|"image"|"audio"}}
- {{"type": "update_clip", "id": "id_do_clip", "properties": {{"scale": float, "x": float, "y": float, "volume": float}}}}
- {{"type": "remove_clip", "id": "id_do_clip"}}
- {{"type": "auto_reportage"}} -> Use esta macro QUANDO o usuário pedir para gerar uma reportagem automática, cortar um vídeo baseado em um áudio, ou fazer o trabalho pesado de edição. Isso fará o frontend disparar a pipeline completa do Diretor!
- {{"type": "generate_broll_image", "prompt": "descrição da imagem", "start": float, "track": "v2"}} -> Use quando o usuário pedir para o Gemini gerar uma imagem (IA) para cobrir uma cena e não houver B-roll na pasta.

Exemplo de retorno:
{{
  "message": "Adicionei o clipe de fogo em 5 segundos conforme pediu!",
  "operations": [
    {{
      "type": "add_clip",
      "track": "v2",
      "start": 5.0,
      "duration": 3.0,
      "path": "C:/Midias/fogo.mp4",
      "clip_type": "video"
    }}
  ]
}}
"""
        
        # Histórico pode ser anexado se existir
        history_text = ""
        if chat_history and len(chat_history) > 0:
            history_text = "\n=== HISTÓRICO RECENTE ===\n"
            for msg in chat_history[-5:]: # ultimas 5
                role = "USER" if msg.get('role') == 'user' else "COPILOT"
                history_text += f"{role}: {msg.get('text')}\n"

        final_prompt = system_prompt + history_text + f"\n=== MENSAGEM DO USUÁRIO ===\n{user_message}\n\nRETORNE APENAS O JSON:"

        try:
            print("[Copiloto] Chamando LLM...", flush=True)
            response_text = self.pipeline._chamar_llm(final_prompt)
            if not response_text:
                return {"message": "Desculpe, o provedor de IA não retornou resposta.", "operations": []}
                
            # Extrair JSON da resposta
            import re
            json_str = re.sub(r'```(?:json)?\s*|\s*```', '', response_text).strip()
            # Tentar encontrar a primeira chave de abertura caso a IA tenha falado algo fora do JSON
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = json_str[start_idx:end_idx+1]
                
            data = json.loads(json_str)
            return {
                "message": data.get("message", "Ação concluída."),
                "operations": data.get("operations", [])
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "message": f"Erro interno ao processar a requisição IA: {str(e)}",
                "operations": []
            }
