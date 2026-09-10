from modal.functions import FunctionCall
import json

job_id = "fc-01M21JM1MVZNVTJSGGW5GRGT03"
try:
    fc = FunctionCall.from_id(job_id)
    res = fc.get(timeout=2.0)
    print("FINISHED")
    print(str(res)[:500])
except Exception as e:
    print(f"NOT FINISHED: {e}")
