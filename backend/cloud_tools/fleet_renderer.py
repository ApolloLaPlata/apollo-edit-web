import os
import json
import requests
import threading

class CloudFleetRenderer:
    """
    Roteador de Renderização em Nuvem do Apollo.
    Esta classe encapsula as ordens do Apollo Studio e as envia para o Gerenciador de Frota.
    """
    def __init__(self):
        self.secrets_path = os.path.join(os.path.dirname(__file__), "fleet_secrets.json")
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_active_modal_account(self):
        try:
            with open(self.secrets_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            modal_ativas = [acc for acc in data.get("modal_accounts", []) if acc["status"] == "active"]
            if not modal_ativas:
                return None
                
            return modal_ativas[0] # Simplificação: Pega a primeira conta ativa. O fleet_balancer fará o round-robin no futuro.
        except:
            return None

    def _get_webhook_url(self, account):
        # Mapeia dinamicamente a URL baseado no email ou ID da conta (solução provisória antes do Router completo)
        workspace = "roxingo" if "roxingo" in account.get("email", "") else "apollolaplata"
        return f"https://{workspace}--apollo-render-router-process-webhook.modal.run"
        
    def _get_file_server_url(self, account):
        workspace = "roxingo" if "roxingo" in account.get("email", "") else "apollolaplata"
        return f"https://{workspace}--apollo-render-router-serve-file.modal.run"

    def request_cloud_render(self, command_str: str, output_name: str, callback=None):
        """
        Envia a ordem de renderização (FFmpeg) para a Nuvem de forma assíncrona.
        """
        def _run():
            acc = self._get_active_modal_account()
            if not acc:
                if callback: callback({"status": "error", "message": "Nenhuma conta Modal ativa na Frota."})
                return
                
            webhook_url = self._get_webhook_url(acc)
            headers = {}
            if acc.get('proxy_secret'):
                headers["Authorization"] = f"Bearer {acc.get('proxy_secret')}"
                
            payload = {
                "action": "render_video",
                "command": command_str,
                "output_name": output_name
            }
            
            try:
                # Timeout alto, pois renderização pode demorar minutos
                response = requests.post(webhook_url, json=payload, headers=headers, timeout=1800)
                if response.status_code == 200:
                    resp_json = response.json()
                    if resp_json.get("status") == "success":
                        # Puxa o arquivo de volta para a máquina local
                        remote_file = resp_json.get("file_path")
                        if remote_file:
                            local_path = self._download_rendered_file(acc, remote_file, output_name)
                            resp_json["local_path"] = local_path
                    if callback: callback(resp_json)
                else:
                    if callback: callback({"status": "error", "message": f"Erro HTTP {response.status_code}: {response.text}"})
            except Exception as e:
                if callback: callback({"status": "error", "message": str(e)})

        t = threading.Thread(target=_run)
        t.start()
        
    def _download_rendered_file(self, account, remote_path, local_filename):
        """
        Utiliza o File Server da Modal para puxar o vídeo pronto.
        """
        file_server_url = self._get_file_server_url(account)
        headers = {}
        if account.get('proxy_secret'):
            headers["Authorization"] = f"Bearer {account.get('proxy_secret')}"
            
        params = {"file_path": remote_path}
        local_dest = os.path.join(self.output_dir, local_filename)
        
        try:
            with requests.get(file_server_url, headers=headers, params=params, stream=True) as r:
                r.raise_for_status()
                with open(local_dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return local_dest
        except Exception as e:
            print(f"Erro ao baixar do File Server: {e}")
            return None
