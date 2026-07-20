"""
i18n.py - Middleware e Funções de Internacionalização
=====================================================
Carrega os JSONs de idioma e expõe uma função t() para traduzir strings
baseadas na preferência do usuário ou no header Accept-Language.
"""

import json
import os
from fastapi import Request
import logging

logger = logging.getLogger("i18n")

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "..", "locales")
translations = {}

def load_locales():
    global translations
    for filename in os.listdir(LOCALES_DIR):
        if filename.endswith(".json"):
            lang = filename.split(".")[0]
            with open(os.path.join(LOCALES_DIR, filename), "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
    logger.info(f"[i18n] Idiomas carregados: {list(translations.keys())}")

load_locales()

def get_locale_from_request(request: Request) -> str:
    """Extrai o idioma preferido do Accept-Language header (fallback pt_BR)"""
    accept_lang = request.headers.get("accept-language", "")
    if "en" in accept_lang.lower():
        return "en_US"
    return "pt_BR"

def t(key_path: str, locale: str = "pt_BR") -> str:
    """
    Traduz uma chave. 
    Ex: t('auth.invalid_credentials', 'en_US')
    """
    keys = key_path.split(".")
    
    # Fallback cascade
    if locale not in translations:
        locale = "pt_BR"
        
    current = translations[locale]
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return key_path # Retorna a chave se não achar a tradução
            
    return str(current)
