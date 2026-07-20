import os
import uuid
import time
from .lightning_fleet import LightningFleetManager

class FFmpegCloudWorker:
    """
    Operário da Nuvem para edições de vídeo brutas.
    Busca uma máquina 'free_cpu' disponível, envia o comando FFmpeg gerado
    pela Apollo, faz o upload dos vídeos de entrada, executa, baixa o resultado
    e passa a "vassoura" para garantir que a máquina desligue com 0 bytes adicionais de Storage.
    """
    def __init__(self, fleet_manager: LightningFleetManager):
        self.fleet = fleet_manager

    def _get_free_cpu_node(self) -> str:
        """
        Busca uma máquina do tipo free_cpu no registry e a inicia se não estiver ligada.
        (Nesta POC, usamos o zygomorphic-green-9lz diretamente).
        Em produção, iteraria sobre as máquinas com role 'free_cpu'.
        """
        # Em uma versão avançada, faríamos um rodízio aqui.
        node_name = "zygomorphic-green-9lz"
        print(f"[FFmpegCloud] Alocando nó: {node_name}")
        self.fleet.start_node(node_name)
        return node_name

    def process_cut(self, input_local_path: str, output_local_path: str, start_time: str, duration: str) -> bool:
        """
        Exemplo de Função 1: Cortar um pedaço de um vídeo.
        """
        return self._run_ffmpeg_job(
            input_paths=[input_local_path],
            output_local_path=output_local_path,
            ffmpeg_args=f"-ss {start_time} -t {duration} -c copy"
        )

    def process_watermark(self, video_local_path: str, watermark_local_path: str, output_local_path: str) -> bool:
        """
        Exemplo de Função 2: Adicionar uma marca d'água.
        """
        return self._run_ffmpeg_job(
            input_paths=[video_local_path, watermark_local_path],
            output_local_path=output_local_path,
            ffmpeg_args="-filter_complex \"overlay=10:10\" -codec:a copy"
        )

    def run_raw_command(self, input_paths: list, output_local_path: str, ffmpeg_args: str) -> bool:
        """
        Executa um comando FFmpeg customizado na nuvem.
        """
        return self._run_ffmpeg_job(input_paths, output_local_path, ffmpeg_args)

    def _run_ffmpeg_job(self, input_paths: list, output_local_path: str, ffmpeg_args: str) -> bool:
        """
        Orquestração principal: Upload -> Processa -> Download -> Limpa -> Desliga.
        """
        node_name = self._get_free_cpu_node()
        
        # Cria um workspace temporário para isolar os arquivos da Apollo e não apagar coisas do sistema da nuvem
        workspace_id = f"apollo_workspace_{uuid.uuid4().hex[:8]}"
        self.fleet.run_task(node_name, f"mkdir -p ~/{workspace_id}")

        # Upload dos arquivos de entrada
        remote_inputs = []
        for i, local_path in enumerate(input_paths):
            ext = os.path.splitext(local_path)[1]
            remote_filename = f"input_{i}{ext}"
            remote_path = f"~/{workspace_id}/{remote_filename}"
            print(f"[FFmpegCloud] Fazendo upload de {local_path}...")
            if not self.fleet.upload_file(node_name, local_path, remote_path):
                return False
            remote_inputs.append(remote_path)

        # Monta a string do ffmpeg
        # Exemplo: ffmpeg -i ~/workspace/input_0.mp4 -i ~/workspace/input_1.png -args... ~/workspace/output.mp4
        inputs_str = " ".join([f"-i {p}" for p in remote_inputs])
        out_ext = os.path.splitext(output_local_path)[1]
        remote_output = f"~/{workspace_id}/output{out_ext}"
        
        ffmpeg_cmd = f"ffmpeg -y {inputs_str} {ffmpeg_args} {remote_output}"
        
        print(f"[FFmpegCloud] Iniciando processamento remoto...")
        if not self.fleet.run_task(node_name, ffmpeg_cmd):
            print("[FFmpegCloud] Falha no FFmpeg.")
            # Limpa antes de sair
            self.fleet.cleanup_node(node_name, f"~/{workspace_id}")
            self.fleet.stop_node(node_name)
            return False

        # Download do resultado
        print(f"[FFmpegCloud] Processamento concluído. Baixando resultado...")
        if not self.fleet.download_file(node_name, remote_output, output_local_path):
            print("[FFmpegCloud] Falha no Download.")
            self.fleet.cleanup_node(node_name, f"~/{workspace_id}")
            self.fleet.stop_node(node_name)
            return False

        # Vassoura: Limpeza Total do Workspace
        print(f"[FFmpegCloud] Passando a vassoura (Cleanup)...")
        self.fleet.cleanup_node(node_name, f"~/{workspace_id}")

        # Desligar para economizar
        self.fleet.stop_node(node_name)
        
        print("[FFmpegCloud] Job finalizado com sucesso 100% Zero-Storage!")
        return True

if __name__ == '__main__':
    # Teste Rápido
    manager = LightningFleetManager()
    worker = FFmpegCloudWorker(manager)
    print("Módulo FFmpegCloudWorker pronto.")
