import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
import google.generativeai as genai
from config_manager import ConfigManager

class AgenciaDeIA:
    """Motor de orquestração Multi-Agente baseado no Fluxograma Master-Worker-Reviewer."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.api_key = self.config.get("api_config.gemini.api_key")
        self.api_keys_list = self.config.get("api_config.gemini.api_keys", [])
        
        if not self.api_key and self.api_keys_list:
            # Pega a última chave ou a que tiver nome Gemini
            gemini_keys = [k for k in self.api_keys_list if "gemini" in k.get("name", "").lower()]
            if gemini_keys:
                self.api_key = gemini_keys[0].get("key")
            else:
                self.api_key = self.api_keys_list[0].get("key")
                
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
        self.gerente_model = "gemini-2.5-pro" # Modelo mais inteligente
        self.mini_model = "gemini-2.5-flash"  # Modelos rápidos e baratos
        
    def _chamar_llm_sincrono(self, system_prompt: str, prompt: str, is_gerente: bool = False, json_mode: bool = False) -> str:
        """Chamada síncrona básica para rodar em Threads."""
        model_name = self.gerente_model if is_gerente else self.mini_model
        
        generation_config = genai.types.GenerationConfig()
        if json_mode:
            generation_config.response_mime_type = "application/json"
            
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config=generation_config
        )
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Agência IA] Erro no LLM ({model_name}): {e}")
            return "{}" if json_mode else "Erro na geração."

    async def _rodar_minis_paralelo(self, mini_tasks: List[Dict[str, str]]) -> List[str]:
        """
        Executa múltiplos 'Chatbots Mini' simultaneamente usando ThreadPool.
        mini_tasks = [{"system": "...", "prompt": "..."}, ...]
        """
        loop = asyncio.get_running_loop()
        resultados = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                loop.run_in_executor(
                    executor, 
                    self._chamar_llm_sincrono, 
                    t.get("system", ""), 
                    t.get("prompt", ""), 
                    False, # is_gerente = False
                    t.get("json_mode", False)
                ) 
                for t in mini_tasks
            ]
            resultados = await asyncio.gather(*futures)
            
        return resultados

    async def executar_fluxo_criacao_fase1(self, resumo_historia: str) -> Dict[str, Any]:
        """
        Fase 1 e 2 do Fluxograma:
        - Gerente divide
        - 7 Minis criam (Personagens, Visual, Trilha, Legendas, Redes, Sinopse, História)
        - Revisor confere
        """
        print("[Agência IA] Iniciando Fase 1: Desdobramento Estrutural...")
        
        # 1. Preparar tarefas para os 7 Minis baseados no resumo
        tarefas = [
            {"system": "Você é um roteirista. Expanda a seguinte ideia em uma História Completa detalhada.", "prompt": resumo_historia},
            {"system": "Você é um criador de personagens. Descreva os personagens principais (físico e psicológico) para esta história.", "prompt": resumo_historia},
            {"system": "Você é um diretor de arte. Crie prompts visuais de quadrinhos/cenas chave para esta história.", "prompt": resumo_historia},
            {"system": "Você é um diretor musical. Sugira a trilha sonora (clima, bpm, instrumentos) para as etapas desta história.", "prompt": resumo_historia},
            {"system": "Você é um copywriter. Crie um título altamente clicável e ideias de legendas para esta história.", "prompt": resumo_historia},
            {"system": "Você é um social media. Crie 3 postagens (Instagram, Twitter, TikTok) baseadas nesta história.", "prompt": resumo_historia},
            {"system": "Você é um roteirista de cinema. Escreva a sinopse curta (logline) e sinopse longa para esta história.", "prompt": resumo_historia}
        ]
        
        # 2. Executar os 7 Minis em paralelo
        print(f"[Agência IA] Disparando {len(tarefas)} Chatbots Mini Econômicos em paralelo...")
        resultados_minis = await self._rodar_minis_paralelo(tarefas)
        
        # Consolidar
        pacote_consolidado = {
            "historia_completa": resultados_minis[0],
            "personagens": resultados_minis[1],
            "prompts_visuais": resultados_minis[2],
            "trilha_sonora": resultados_minis[3],
            "titulo_legendas": resultados_minis[4],
            "redes_sociais": resultados_minis[5],
            "sinopse": resultados_minis[6]
        }
        
        # 3. Conferência (O Revisor)
        print("[Agência IA] Chat Bot Gerente Conferência avaliando qualidade...")
        prompt_revisor = f"Avalie a qualidade deste pacote de conteúdo. Se houver falhas graves ou fuga do tema inicial ('{resumo_historia}'), retorne status 'rejeitado'. Caso contrário, retorne 'aprovado'.\nPacote: {json.dumps(pacote_consolidado)}"
        
        revisao_txt = self._chamar_llm_sincrono(
            system_prompt="Você é o Gerente Revisor. Retorne um JSON válido com a chave 'status' sendo 'aprovado' ou 'rejeitado', e 'motivo' se rejeitado.",
            prompt=prompt_revisor,
            is_gerente=True,
            json_mode=True
        )
        
        try:
            revisao = json.loads(revisao_txt)
        except:
            revisao = {"status": "aprovado"}
            
        if revisao.get("status") == "rejeitado":
            print("[Agência IA] ⚠️ Pacote Rejeitado pelo Revisor! Motivo:", revisao.get("motivo"))
            # Num sistema real robusto, faríamos um loop. Por enquanto retornamos o erro para o usuário.
            return {"sucesso": False, "motivo": revisao.get("motivo"), "dados": pacote_consolidado}
            
        print("[Agência IA] ✅ Pacote Aprovado!")
        return {"sucesso": True, "dados": pacote_consolidado}

    async def executar_fluxo_roteiros_cenas_fase3(self, pacote_fase1: Dict[str, Any], dias: int = 7) -> Dict[str, Any]:
        """
        Fase 3: O Gerente de Roteiro e Prompt expande em múltiplos dias (ex: 7 dias)
        Aciona (dias * 2) Minis: Metade para Roteiro e Metade para Cenas Visuais.
        """
        print(f"[Agência IA] Iniciando Fase 3: Geração em Massa para {dias} dias/episódios...")
        
        historia_base = pacote_fase1.get("historia_completa", "")
        
        tarefas = []
        # Criação de tarefas para Roteiros e Prompts Visuais
        for dia in range(1, dias + 1):
            tarefas.append({
                "system": f"Você é roteirista. Crie APENAS o roteiro detalhado do Episódio {dia} (Parte {dia} de {dias}) baseado na história.", 
                "prompt": historia_base
            })
            tarefas.append({
                "system": f"Você é diretor de arte. Extraia APENAS os prompts visuais/cenários para o Episódio {dia} (Parte {dia} de {dias}) no formato JSON. Estrutura: {{\"cenas\": [ {{\"prompt\": \"...\"}} ]}}", 
                "prompt": historia_base,
                "json_mode": True
            })
            
        print(f"[Agência IA] Disparando {len(tarefas)} Chatbots Mini Econômicos em paralelo...")
        resultados_minis = await self._rodar_minis_paralelo(tarefas)
        
        roteiros_finais = {}
        cenas_visuais = {}
        
        for dia in range(1, dias + 1):
            idx_roteiro = (dia - 1) * 2
            idx_cena = ((dia - 1) * 2) + 1
            
            roteiros_finais[f"DIA_{dia}"] = resultados_minis[idx_roteiro]
            try:
                cenas_visuais[f"DIA_{dia}"] = json.loads(resultados_minis[idx_cena])
            except:
                cenas_visuais[f"DIA_{dia}"] = {"cenas": [{"prompt": resultados_minis[idx_cena]}]}
                
        print("[Agência IA] ✅ Fase 3 Concluída! Visão Completa gerada.")
        
        return {
            "roteiros": roteiros_finais,
            "cenas_visuais": cenas_visuais
        }

# Função wrapper para testar/usar fora de async contexts
def disparar_agencia(resumo: str):
    config = ConfigManager()
    agencia = AgenciaDeIA(config)
    
    async def run():
        res1 = await agencia.executar_fluxo_criacao_fase1(resumo)
        if res1["sucesso"]:
            res2 = await agencia.executar_fluxo_roteiros_cenas_fase3(res1["dados"], dias=7)
            return {"fase1": res1, "fase3": res2}
        return res1
        
    return asyncio.run(run())
