import modal
from backend.cloud_tools.modal_app import app

# Importando todas as engines para atrelá-las ao mesmo app 'apollo-render-router'
# Dessa forma, quando rodarmos 'modal deploy deploy_engines.py', a Modal subirá todas as rotas juntas
# sem deletar os endpoints anteriores.

import backend.cloud_tools.engines.tts_engine
import backend.cloud_tools.engines.stt_engine
import backend.cloud_tools.engines.f5_engine
import backend.cloud_tools.engines.xtts_engine
import backend.cloud_tools.engines.melo_engine
import backend.cloud_tools.engines.fish_engine

# Nota: Moshi Engine tem um app separado ('apollo-moshi-engine') por causa dos requisitos pesados e isolados do WebSocket.
# Ele continua sendo feito deploy via: modal deploy backend.cloud_tools.engines.moshi_engine
