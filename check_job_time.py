from modal.functions import FunctionCall
import json

job_id = "fc-01M21JM1MVZNVTJSGGW5GRGT03"
try:
    fc = FunctionCall.from_id(job_id)
    print(f"Created at: {fc.created_at}")
except Exception as e:
    print(f"Error: {e}")
