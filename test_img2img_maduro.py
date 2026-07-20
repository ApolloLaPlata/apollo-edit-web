import requests, base64, json, time, os

def test_nicolas_maduro():
    image_path = r'C:\Users\v5est\Downloads\character_turnaround_1777218163561.png'
    out_dir = r'C:\Users\v5est\Downloads'
    out_filename = 'maduro_preso_teste.png'
    out_path = os.path.join(out_dir, out_filename)

    if not os.path.exists(image_path):
        print("Imagem base não encontrada no Downloads!")
        return

    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        'prompt': 'A dramatic cartoon drawing of Nicolas Maduro being arrested and escorted into a United States helicopter, intense action scene, high quality illustration',
        'reference_images_base64': [img_b64],
        'format': 'horizontal',
        'model': 'flux2-universal'
    }

    print('Enviando requisição Img2Img para Modal...')
    start_time = time.time()
    
    try:
        r = requests.post('https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image', json=payload, stream=True)
        print(f"Status Code: {r.status_code}")
        
        final_data = None
        for line in r.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if "status" in decoded and "image_base64" in decoded:
                    try:
                        final_data = json.loads(decoded)
                        break
                    except:
                        pass
                else:
                    print(decoded)
                    
        total_time = time.time() - start_time
        
        if final_data and final_data.get("status") == "success":
            render_time = final_data.get("render_time_seconds", 0)
            cold_start_and_network = total_time - render_time
            
            # Modal H100 cost: ~$4.68 / hr = ~$0.0013 / sec
            # Considerando o keep_alive de 60s
            cost_per_second = 4.68 / 3600
            total_billed_time = total_time + 60 # tempo do request + 60s q a maquina fica viva idle
            estimated_cost = total_billed_time * cost_per_second
            
            print("\n===============================")
            print("RESULTADOS DO TESTE MODAL H100")
            print("===============================")
            print(f"Tempo Total (Usuário): {total_time:.2f}s")
            print(f"Tempo de Geração Pura (GPU): {render_time:.2f}s")
            print(f"Tempo de Cold Start + Rede: {cold_start_and_network:.2f}s")
            print(f"Custo Estimado (incluindo idle de 60s): ${estimated_cost:.4f} USD")
            
            b64_img = final_data["image_base64"]
            with open(out_path, "wb") as f_out:
                f_out.write(base64.b64decode(b64_img))
            print(f"\nImagem de teste salva com sucesso em:")
            print(out_path)
            
        else:
            print("Erro na resposta ou sem dados de imagem:", final_data)

    except Exception as e:
        print("Exception:", e)

if __name__ == '__main__':
    test_nicolas_maduro()
