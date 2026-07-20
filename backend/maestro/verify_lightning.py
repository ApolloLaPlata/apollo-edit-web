if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from lightning_sdk import Studio, Machine
    
    load_dotenv()
    
    api_key = os.getenv("LIGHTNING_API_KEY")
    user_id = os.getenv("LIGHTNING_USER_ID")
    
    print(f"Buscando com API KEY terminada em: {api_key[-4:] if api_key else 'Nenhuma'}")
    
    # A SDK deve usar as variÃ¡veis de ambiente automaticamente
    try:
        print("Conectando Ã  Lightning AI...")
        import lightning as L
        # We don't have to authenticate manually if LIGHTNING_API_KEY is set.
        studios = Studio.list()
        print("Studios encontrados:")
        for s in studios:
            print(f"- {s.name} (Status: {s.status})")
        if not studios:
            print("Nenhum Studio encontrado. A conexÃ£o funcionou, mas a conta estÃ¡ vazia.")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
    
