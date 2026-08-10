import modal
print(modal.__version__)
try:
    f = modal.Function.from_name("apollo-render-router", "F5TTSEngine.generate_voice")
    print("from_name works")
except Exception as e:
    print(f"Error: {e}")
