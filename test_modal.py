import modal
cls = modal.Cls.from_name("apollo-render-router", "AceStep15Engine")()
try:
    print(dir(cls))
except Exception as e:
    print("DIR ERROR:", e)
