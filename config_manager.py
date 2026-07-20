import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """Gerenciador de configurações do Descarga News Editor"""
    _instance = None
    
    def __new__(cls, config_file: str = "config.json"):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_file: str = "config.json"):
        if getattr(self, '_initialized', False) and config_file == "config.json":
            # If already initialized with a specific workspace, ignore default calls
            return
            
        self.config_file = config_file
        self.config = self._load_config()
        self._initialized = True
        
    def get_admin_config_file(self) -> str:
        """Retorna o caminho absoluto do arquivo de configuração administrativo central"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "admin_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo JSON local e mescla com as globais"""
        admin_file = self.get_admin_config_file()
        admin_config = {}
        
        # Carrega ou cria config administrativa
        if os.path.exists(admin_file):
            try:
                with open(admin_file, 'r', encoding='utf-8') as f:
                    admin_config = json.load(f)
            except:
                admin_config = {}
                
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                changed = False
                
                # Migração das chaves locais para as globais (apenas se a global estiver vazia)
                if not admin_config:
                    if "api_config" in config:
                        admin_config["api_config"] = config["api_config"]
                    if "vps_config" in config:
                        admin_config["vps_config"] = config["vps_config"]
                    
                    if admin_config:
                        with open(admin_file, 'w', encoding='utf-8') as f:
                            json.dump(admin_config, f, indent=2, ensure_ascii=False)
                
                # Força valores padrão globais se ainda não existirem
                if "api_config" not in admin_config:
                    admin_config["api_config"] = {
                        "voicemaker": {"base_url": "https://developer.voicemaker.in/voice/api", "api_keys": []},
                        "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-3.5-flash", "api_keys": []},
                        "chatgpt": {"base_url": "https://api.openai.com/v1", "api_keys": []},
                        "openrouter": {"base_url": "https://openrouter.ai/api/v1", "api_keys": []},
                        "grok": {"base_url": "https://api.x.ai/v1", "api_keys": []}
                    }
                if "vps_config" not in admin_config:
                    admin_config["vps_config"] = {
                        "moss_tts": {"url": "http://localhost:8000", "token": ""},
                        "applio_rvc": {"url": "http://localhost:8001", "token": ""}
                    }
                
                # INJEÇÃO TRANSPARENTE: O painel achará que essas chaves estão no config local
                config["api_config"] = admin_config.get("api_config", {})
                config["vps_config"] = admin_config.get("vps_config", {})

                # --- MIGRATION BLOCK (Local) ---
                if "music_factory" not in config:
                    config["music_factory"] = {
                        "channel_context": "Este é um canal de instrumentais e beats. As músicas não possuem vocais. O objetivo é vender o beat na BeatStars.",
                        "metadata_example": "Title: [Original Name] | Type Beat\\nDescription: Buy this beat on BeatStars! Link: https://beatstars.com/meucanal\\nTags: type beat, instrumental"
                    }
                    changed = True

                if "shortcuts" not in config:
                    config["shortcuts"] = {}
                    changed = True

                if "perfis_diretor" not in config:
                    config["perfis_diretor"] = {}
                    changed = True

                if changed:
                    # Removemos as chaves globais antes de salvar o local modificado
                    local_to_save = dict(config)
                    local_to_save.pop("api_config", None)
                    local_to_save.pop("vps_config", None)
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(local_to_save, f, indent=2, ensure_ascii=False)
                        
                return config
            else:
                # Cria configuração padrão se o arquivo não existir
                return self._create_default_config()
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return self._create_default_config()
    def _create_default_config(self) -> Dict[str, Any]:
        """Cria configuração padrão"""
        default_config = {
            "app_info": {
                "name": "Descarga News Editor",
                "version": "1.0.0",
                "description": "Editor de vídeo automatizado para o canal Descarga News"
            },
            "personagens": {
                "Rafael Descargas": {
                    "video_source": "../Midias\\Personagens\\Rafael Descarga\\RAFAEL_DESCARGA_NORMAL.mp4",
                    "vozes_voicemaker": "proplus-DJ_Jax",
                    "posicao_pip": {"x": 25, "y": "bottom", "offset": 25, "escala": 0.25}
                }
            },
            "backgrounds": {
                "Padrão": "../Midias\\BG PARA VIDEOS DO DESCARGA NEWS\\BG PARA VIDEOS DO DESCARGA NEWS_1.mp4"
            },
            "paths": {
                "output_dir": "../Midias\\Outputs",
                "temp_dir": "../Midias\\Temp",
                "assets_dir": "../Midias"
            },
            "subtitles": {
                "enabled": False,
                "font_name": "Arial",
                "font_size": 24,
                "text_color": "#FFFFFF",
                "outline_color": "#000000",
                "outline": 2,
                "shadow": 0,
                "alignment": "Bottom-Center",
                "margin_v": 20,
                "margin_l": 20,
                "margin_r": 20
            },
            "capa": {
                "mode": "none",  # none, horizontal, vertical, auto
                "path_h": "",
                "path_v": ""
            },
            "music_factory": {
                "channel_context": "Este é um canal de instrumentais e beats. As músicas não possuem vocais. O objetivo é vender o beat na BeatStars.",
                "metadata_example": "Title: [Original Name] | Type Beat\\nDescription: Buy this beat on BeatStars! Link: https://beatstars.com/meucanal\\nTags: type beat, instrumental"
            },
            "api_config": {},
            "vps_config": {},
            "shortcuts": {},
            "perfis_diretor": {}
        }
        
        # Salva configuração padrão
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Salva configurações no arquivo JSON e gerencia a separação global"""
        try:
            config_to_save = config if config is not None else self.config
            
            # 1. Extrai as configurações globais
            admin_config = {}
            if "api_config" in config_to_save and config_to_save["api_config"]:
                admin_config["api_config"] = config_to_save["api_config"]
            if "vps_config" in config_to_save and config_to_save["vps_config"]:
                admin_config["vps_config"] = config_to_save["vps_config"]
                
            # Salva o arquivo global
            if admin_config:
                admin_file = self.get_admin_config_file()
                existing_admin = {}
                if os.path.exists(admin_file):
                    try:
                        with open(admin_file, 'r', encoding='utf-8') as f:
                            existing_admin = json.load(f)
                    except:
                        pass
                
                existing_admin.update(admin_config)
                with open(admin_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_admin, f, indent=2, ensure_ascii=False)
            
            # 2. Salva o arquivo local (removendo chaves globais)
            local_config_to_save = dict(config_to_save)
            local_config_to_save.pop("api_config", None)
            local_config_to_save.pop("vps_config", None)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(local_config_to_save, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração usando notação de ponto (ex: 'personagens.Rafael Descargas.video_source')"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Define valor de configuração usando notação de ponto"""
        keys = key.split('.')
        config = self.config
        
        # Navega até o nível anterior ao último
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Define o valor final
        config[keys[-1]] = value
        return self.save_config()
    
    def get_personagem(self, nome: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração de um personagem específico (Busca Inteligente / Similaridade)"""
        import re
        import difflib
        
        personagens = self.get("personagens", {})
        if not personagens or not nome:
            return None
            
        # 1. Busca Exata
        if nome in personagens:
            return personagens[nome]
            
        # 2. Busca Exata Case-Insensitive
        nome_lower = nome.lower()
        for key, p_config in personagens.items():
            if key.lower() == nome_lower:
                return p_config
                
        # 3. Busca por Interseção de Palavras (Tokens)
        def get_tokens(s):
            return set(re.findall(r'\w+', s.lower()))
            
        nome_tokens = get_tokens(nome)
        best_match = None
        max_overlap = 0
        
        for key, p_config in personagens.items():
            key_tokens = get_tokens(key)
            if not key_tokens or not nome_tokens:
                continue
            
            overlap = len(nome_tokens.intersection(key_tokens))
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = p_config
                
        if max_overlap > 0:
            return best_match
            
        # 4. Busca por Similaridade (Fuzzy)
        matches = difflib.get_close_matches(nome, personagens.keys(), n=1, cutoff=0.5)
        if matches:
            return personagens[matches[0]]
            
        return None

    def get_background(self, nome: str) -> Optional[str]:
        """Obtém caminho de um background específico"""
        return self.get(f"backgrounds.{nome}")
    
    def get_path(self, tipo: str) -> Optional[str]:
        """Obtém caminho de diretório específico"""
        return self.get(f"paths.{tipo}")
    
    def get_api_config(self, service: str, key: str = None) -> Any:
        """Obtém configuração da API específica"""
        if key:
            return self.get(f"api_config.{service}.{key}")
        return self.get(f"api_config.{service}")
    
    def get_voicemaker_config(self, key: str = None) -> Any:
        """Obtém configuração específica do VoiceMaker"""
        return self.get_api_config("voicemaker", key)
    
    def get_gemini_config(self, key: str = None) -> Any:
        """Obtém configuração específica do Gemini"""
        return self.get_api_config("gemini", key)
    
    def update_personagem(self, nome: str, config: Dict[str, Any]) -> bool:
        """Atualiza configuração de um personagem"""
        return self.set(f"personagens.{nome}", config)
    
    def add_personagem(self, nome: str, config: Dict[str, Any]) -> bool:
        """Adiciona novo personagem"""
        return self.set(f"personagens.{nome}", config)
    
    def remove_personagem(self, nome: str) -> bool:
        """Remove personagem da configuração"""
        try:
            del self.config["personagens"][nome]
            return self.save_config()
        except KeyError:
            return False

    def resolve_path(self, path_str: str) -> str:
        """Resolve caminhos que contêm atalhos definidos no formato {NOME_ATALHO}"""
        if not path_str or not isinstance(path_str, str):
            return path_str
            
        shortcuts = self.get("shortcuts", {})
        if not shortcuts:
            return path_str
            
        import re
        matches = re.findall(r'\{([^}]+)\}', path_str)
        
        resolved_path = path_str
        for key in matches:
            if key in shortcuts:
                resolved_path = resolved_path.replace(f"{{{key}}}", shortcuts[key])
                
        if resolved_path != path_str:
            resolved_path = os.path.normpath(resolved_path)
            
        return resolved_path

    def get_ffmpeg_path(self) -> str:
        """Retorna o caminho do ffmpeg.exe embutido na pasta bin (para versão comercial) ou o fallback do sistema."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(base_dir, "bin", "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        return "ffmpeg"

    def get_ffprobe_path(self) -> str:
        """Retorna o caminho do ffprobe.exe embutido na pasta bin (para versão comercial) ou o fallback do sistema."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffprobe = os.path.join(base_dir, "bin", "ffprobe.exe")
        if os.path.exists(local_ffprobe):
            return local_ffprobe
        return "ffprobe"

    def mark_api_key_exhausted(self, service: str, key_string: str) -> bool:
        """Marca uma chave de API como esgotada (status: exhausted) e salva."""
        api_keys = self.get(f"api_config.{service}.api_keys", [])
        if not api_keys:
            return False
        changed = False
        for k in api_keys:
            if k.get("key") == key_string and k.get("status") != "exhausted":
                k["status"] = "exhausted"
                changed = True
        if changed:
            return self.set(f"api_config.{service}.api_keys", api_keys)
        return False

    def update_api_key_spend(self, service: str, key_string: str, cost: float) -> bool:
        """Adiciona um custo ao valor 'estimated_spend' de uma chave de API."""
        if cost <= 0:
            return False
        api_keys = self.get(f"api_config.{service}.api_keys", [])
        if not api_keys:
            return False
        changed = False
        for k in api_keys:
            if k.get("key") == key_string:
                k["estimated_spend"] = k.get("estimated_spend", 0.0) + cost
                # Auto-exhaust rule Se estourou o budget que o usuario definiu localmente (opcional)
                balance_limit = k.get("balance_limit", 0.0)
                if balance_limit > 0.0 and k["estimated_spend"] >= balance_limit:
                    k["status"] = "exhausted"
                changed = True
        if changed:
            return self.set(f"api_config.{service}.api_keys", api_keys)
        return False
