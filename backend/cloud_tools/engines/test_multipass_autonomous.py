import os
import modal
import sys

# Script para testar a transferência de emoção do F5-TTS para o XTTS
# 1. F5-TTS gera um áudio de raiva em PT-BR (sotaque americanizado).
# 2. XTTS usa esse áudio como referência para gerar uma nova frase em PT-BR perfeito.

print("=== Iniciando Teste de Multipass (F5 -> XTTS) ===")
print("Este script deve ser rodado via Modal ou adaptado para chamar as engines remotas.")

