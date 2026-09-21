import modal

# O App central que compartilha o estado para todas as funções e engines
from backend.cloud_tools.core_app import app

from backend.cloud_tools.engines.comfy_experimental import *
from backend.cloud_tools.engines.vllm_engine import *
from backend.cloud_tools.engines.universal_engine import *
from backend.cloud_tools.engines.stable_audio_engine import *
from backend.cloud_tools.engines.minimax_engine import *
from backend.cloud_tools.engines.ace_step_python_engine import *
from backend.cloud_tools.engines.wan_engine import *
from backend.cloud_tools.engines.sadtalker_engine import *
from backend.cloud_tools.engines.universal_comfy_engine import *
from backend.cloud_tools.engines.deforum_engine import *

from backend.cloud_tools.engines.qwen_image_engine import *
from backend.cloud_tools.engines.qwen_image_edit_engine import *
from backend.cloud_tools.engines.flux_txt2img_engine import *
from backend.cloud_tools.engines.flux_engine import *

from backend.cloud_tools.engines.hunyuan_engine import *

from backend.cloud_tools.engines.ltx_engine import *

from backend.cloud_tools.apollo_modal_engine import *
