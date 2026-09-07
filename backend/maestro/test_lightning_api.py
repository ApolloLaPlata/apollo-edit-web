if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from openai import OpenAI
    
    load_dotenv()
    
    # Lightning AI fornece um endpoint compatível com a OpenAI para o "Plano A"
    # A documentação deles usa o endpoint litapi ou api.lightning.ai
    # Mas se eles não suportam isso diretamente na chave de CLI, testaremos.
    
    api_key = os.getenv("LIGHTNING_API_KEY")
    
    if not api_key:
        print("Erro: Chave não encontrada no .env")
        exit()
    
    try:
        print("Iniciando teste de Roteirista IA (LLM) no Lightning AI (Plano A)...")
        
        # A Lightning usa a litai library, mas por baixo dos panos é OpenAI compatível.
        # Se o endpoint de base deles não funcionar assim, ajustaremos.
        # O endpoint para modelos serverless na Lightning
        client = OpenAI(
            base_url="https://api.lightning.ai/v1",
            api_key=api_key
        )
    
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf", # Um modelo comum em provedores serverless, ou tentamos outro se falhar
            messages=[
                {"role": "user", "content": "Diga 'Conexão com a Lightning AI estabelecida com sucesso! Apollo Edit Web está online.' e nada mais."}
            ],
            max_tokens=50
        )
        
        print("\nRESPOSTA DA LIGHTNING AI:")
        print("=" * 50)
        print(response.choices[0].message.content)
        print("=" * 50)
        print("\n✅ O PLANO A (Serverless Text API) ESTÁ FUNCIONANDO PERFEITAMENTE!")
    
    except Exception as e:
        print(f"\n❌ Erro ao conectar na API de Texto: {e}")
        print("Isso geralmente significa que precisamos usar a biblioteca 'litai' específica ou o endpoint exato.")
    
