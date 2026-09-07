import modal

# O App central que compartilha o estado para todas as funções e engines
app = modal.App("apollo-render-router")

from backend.cloud_tools.engines.comfy_experimental import *
from backend.cloud_tools.engines.f5_engine import *
from backend.cloud_tools.engines.vllm_engine import *
from backend.cloud_tools.engines.stt_engine import *
from backend.cloud_tools.engines.universal_engine import *
from backend.cloud_tools.engines.xtts_engine import *

# Audio Lab Engines
from backend.cloud_tools.engines.stable_audio_engine import *
from backend.cloud_tools.engines.minimax_engine import *
from backend.cloud_tools.engines.ace_step_python_engine import *
