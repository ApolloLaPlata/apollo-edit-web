import modal

print("Trying Cls.from_name...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
    print("Success! Cls acquired.")
except Exception as e:
    print(f"Error: {e}")
