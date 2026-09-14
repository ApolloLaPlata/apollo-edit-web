import modal
cls = modal.Cls.from_name("apollo-render-router", "StableAudioEngine")
print("Chamando func...")
res = cls().generate_audio.remote("test", 10.0, 8, 0)
print(f"Sucesso, tamanho do arquivo: {len(res)}")
