import customtkinter as ctk
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import subprocess
import glob
import re
import random
from music_video_engine import MusicVideoEngine
from gemini_api import GeminiAPI

class AbaFabricaClipes(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.base_dir = self.config_manager.workspace_dir
        
        self.sub_notebook = ttk.Notebook(self)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba 1: Gerador Lote
        self.frame_gerador = ctk.CTkFrame(self.sub_notebook)
        self.sub_notebook.add(self.frame_gerador, text="🎵 Gerador de Vídeos Musicais")
        self._construir_gerador()
        
        # Aba 2: Compilador 24h
        self.frame_compilador = ctk.CTkFrame(self.sub_notebook)
        self.sub_notebook.add(self.frame_compilador, text="⏳ Compilador (Lives 24h)")
        self._construir_compilador()
        
        # Variables state
        self.music_folders = [] # list of dicts

    def _construir_gerador(self):
        # 1. Configurações Base
        frame_configs = ctk.CTkLabelFrame(self.frame_gerador, text="1. Configuração dos Diretórios")
        frame_configs.pack(fill=tk.X, padx=10, pady=10)
        
        # Pasta Suno
        ctk.CTkLabel(frame_configs, text="Pasta Raiz Músicas (Suno):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.var_pasta_suno = tk.StringVar(value=self.config_manager.get("fabrica_clipes.suno_dir", ""))
        ctk.CTkEntry(frame_configs, textvariable=self.var_pasta_suno, width=60).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(frame_configs, text="Procurar...", command=self._procurar_pasta_suno).grid(row=0, column=2, padx=5, pady=5)
        
        # Pasta Backgrounds
        ctk.CTkLabel(frame_configs, text="Pasta de Backgrounds Base:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.var_pasta_bgs = tk.StringVar(value=self.config_manager.get("fabrica_clipes.bg_dir", ""))
        ctk.CTkEntry(frame_configs, textvariable=self.var_pasta_bgs, width=60).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(frame_configs, text="Procurar...", command=self._procurar_pasta_bgs).grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(frame_configs, text="🔄 Carregar Músicas", command=self._carregar_musicas).grid(row=2, column=0, columnspan=3, pady=10)

        # 2. Tabela de Músicas
        frame_tabela = ctk.CTkLabelFrame(self.frame_gerador, text="2. Músicas Encontradas")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree_musicas = ttk.Treeview(frame_tabela, columns=("musica", "audio", "txt", "status"), show="headings")
        self.tree_musicas.heading("musica", text="Nome da Música")
        self.tree_musicas.heading("audio", text="Arquivo de Áudio")
        self.tree_musicas.heading("txt", text="Prompt (TXT)")
        self.tree_musicas.heading("status", text="Status")
        
        self.tree_musicas.column("musica", width=200)
        self.tree_musicas.column("audio", width=150)
        self.tree_musicas.column("txt", width=100, anchor='center')
        self.tree_musicas.column("status", width=100, anchor='center')
        
        scroll = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=self.tree_musicas.yview)
        self.tree_musicas.configure(yscrollcommand=scroll.set)
        
        self.tree_musicas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 3. Ações
        frame_acoes = ctk.CTkFrame(self.frame_gerador)
        frame_acoes.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(frame_acoes, text="Template Visual:").pack(side=tk.LEFT, padx=5)
        self.var_template = tk.StringVar()
        self.combo_templates = ctk.CTkOptionMenu(frame_acoes, variable=self.var_template, width=250)
        self.combo_templates.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(frame_acoes, text="🔄 Atualizar Lista", command=self._atualizar_lista_templates).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(frame_acoes, text="Capa IA:").pack(side=tk.LEFT, padx=(15, 5))
        self.var_formato_capa = tk.StringVar()
        self.combo_formato_capa = ctk.CTkOptionMenu(frame_acoes, variable=self.var_formato_capa, width=200)
        self.combo_formato_capa['values'] = ["Quadrada (1:1)", "Vertical (9:16)", "Horizontal (16:9)", "Não gerar capa"]
        self.combo_formato_capa.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(frame_acoes, text="🚀 Gerar Vídeos em Lote", command=self._iniciar_geracao).pack(side=tk.RIGHT, padx=5)
        
        self._atualizar_lista_templates()

    def _atualizar_lista_templates(self):
        perfis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis_templates")
        if not os.path.exists(perfis_dir):
            return
            
        templates = [f for f in os.listdir(perfis_dir) if f.endswith('.json')]
        self.combo_templates['values'] = ["Aleatório (Auto)"] + templates
        if not self.var_template.get():
            self.combo_templates.set("Aleatório (Auto)")

    def _procurar_pasta_suno(self):
        d = filedialog.askdirectory(title="Selecione a Pasta Raiz das Músicas")
        if d:
            self.var_pasta_suno.set(d)
            self.config_manager.set("fabrica_clipes.suno_dir", d)

    def _procurar_pasta_bgs(self):
        d = filedialog.askdirectory(title="Selecione a Pasta de Vídeos Base")
        if d:
            self.var_pasta_bgs.set(d)
            self.config_manager.set("fabrica_clipes.bg_dir", d)

    def _carregar_musicas(self):
        suno_dir = self.var_pasta_suno.get()
        if not suno_dir or not os.path.exists(suno_dir):
            messagebox.showerror("Erro", "Pasta do Suno inválida.")
            return
            
        for i in self.tree_musicas.get_children():
            self.tree_musicas.delete(i)
            
        self.music_folders = []
        
        for p in os.listdir(suno_dir):
            caminho_pasta = os.path.join(suno_dir, p)
            if os.path.isdir(caminho_pasta):
                arquivos = os.listdir(caminho_pasta)
                # Tenta achar .wav ou .mp3, .txt e imagens
                audio_file = next((f for f in arquivos if f.endswith(('.wav', '.mp3'))), None)
                txt_file = next((f for f in arquivos if f.endswith('.txt')), None)
                cover_file = next((f for f in arquivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
                
                if audio_file:
                    self.music_folders.append({
                        "nome": p,
                        "pasta": caminho_pasta,
                        "audio": os.path.join(caminho_pasta, audio_file),
                        "txt": os.path.join(caminho_pasta, txt_file) if txt_file else None,
                        "cover": os.path.join(caminho_pasta, cover_file) if cover_file else None,
                        "status": "Pendente"
                    })
                    
        for m in self.music_folders:
            tem_txt = "Sim" if m['txt'] else "Não"
            self.tree_musicas.insert("", tk.END, values=(m['nome'], os.path.basename(m['audio']), tem_txt, m['status']))

    def _iniciar_geracao(self):
        if not self.music_folders:
            messagebox.showwarning("Aviso", "Nenhuma música carregada na tabela.")
            return
        
        bg_dir = self.var_pasta_bgs.get()
        if not bg_dir or not os.path.exists(bg_dir):
            messagebox.showerror("Erro", "Pasta de backgrounds inválida.")
            return
            
        # Pega as músicas da tabela
        musicas_selecionadas = []
        for child in self.tree_musicas.get_children():
            valores = self.tree_musicas.item(child, 'values')
            nome = valores[0]
            # acha no dict
            musica_data = next((m for m in self.music_folders if m['nome'] == nome), None)
            if musica_data:
                musicas_selecionadas.append((child, musica_data))
                
        if not musicas_selecionadas:
            return

        template_file = self.var_template.get()
        if not template_file:
            messagebox.showerror("Erro", "Selecione um Template Visual.")
            return

        formato_capa = self.var_formato_capa.get()
        if not formato_capa:
            messagebox.showerror("Erro", "Selecione uma opção para a Capa IA.")
            return

        threading.Thread(target=self._worker_gerar, args=(bg_dir, musicas_selecionadas, template_file, formato_capa), daemon=True).start()

    def _worker_gerar(self, bg_dir, musicas_selecionadas, template_file, formato_capa):
        engine = MusicVideoEngine(self.config_manager.workspace_dir)
        gemini = GeminiAPI(self.config_manager)
        
        # Cria pasta outputs/fabrica_clipes se não existir
        out_dir = os.path.join(self.config_manager.workspace_dir, "outputs", "fabrica_clipes")
        os.makedirs(out_dir, exist_ok=True)
        
        for item_id, m_data in musicas_selecionadas:
            try:
                self.tree_musicas.set(item_id, "status", "Processando...")
                
                # Nome de saida limpo
                nome_limpo = "".join(c for c in m_data['nome'] if c.isalnum() or c in " _-").strip()
                # O usuário pediu para salvar DENTRO da pasta de origem
                out_path = os.path.join(m_data['pasta'], f"{nome_limpo}.mp4")
                
                song_name = m_data['nome']
                
                # 1. Metadados IA
                channel_context = self.config_manager.get("music_factory.channel_context", "")
                metadata_example = self.config_manager.get("music_factory.metadata_example", "")
                
                if m_data['txt']:
                    meta_path = os.path.join(m_data['pasta'], "metadata.json")
                    if not os.path.exists(meta_path):
                        self.tree_musicas.set(item_id, "status", "Gerando IA...")
                        with open(m_data['txt'], 'r', encoding='utf-8') as f:
                            prompt_text = f.read()
                        res = gemini.generate_music_metadata(prompt_text, song_name, channel_context, metadata_example)
                        if res:
                            # Limpa os blocos markdown se existirem
                            res = res.replace("```json", "").replace("```", "").strip()
                            try:
                                # Validate JSON
                                json_data = json.loads(res)
                                with open(meta_path, 'w', encoding='utf-8') as mf:
                                    json.dump(json_data, mf, ensure_ascii=False, indent=4)
                                if "title" in json_data:
                                    song_name = json_data["title"]
                                
                                aspect_ratio = None
                                if formato_capa == "Quadrada (1:1)": aspect_ratio = "1:1"
                                elif formato_capa == "Vertical (9:16)": aspect_ratio = "9:16"
                                elif formato_capa == "Horizontal (16:9)": aspect_ratio = "16:9"

                                if "image_prompt" in json_data:
                                    prompt_capa_path = os.path.join(m_data['pasta'], "prompt_capa.txt")
                                    with open(prompt_capa_path, 'w', encoding='utf-8') as pcf:
                                        pcf.write(json_data["image_prompt"])
                                        
                                    if aspect_ratio:
                                        cover_ia_path = os.path.join(m_data['pasta'], "cover_ia.jpg")
                                        if not os.path.exists(cover_ia_path):
                                            self.tree_musicas.set(item_id, "status", f"Gerando Capa {aspect_ratio}...")
                                            gemini.generate_image(json_data["image_prompt"], output_path=cover_ia_path, aspect_ratio=aspect_ratio)
                                        
                                        if os.path.exists(cover_ia_path):
                                            m_data['cover'] = cover_ia_path
                                        
                                if "lyrics" in json_data:
                                    lyrics_path = os.path.join(m_data['pasta'], "lyrics_ia.txt")
                                    with open(lyrics_path, 'w', encoding='utf-8') as lf:
                                        lf.write(json_data["lyrics"])
                                if "broll_prompts" in json_data:
                                    brolls_path = os.path.join(m_data['pasta'], "broll_prompts.json")
                                    with open(brolls_path, 'w', encoding='utf-8') as bf:
                                        json.dump(json_data["broll_prompts"], bf, ensure_ascii=False, indent=4)
                            except Exception as e:
                                print(f"Falha ao processar JSON da IA: {e}")
                    else:
                        try:
                            with open(meta_path, 'r', encoding='utf-8') as mf:
                                meta = json.load(mf)
                                if "title" in meta:
                                    song_name = meta["title"]
                                    
                                aspect_ratio = None
                                if formato_capa == "Quadrada (1:1)": aspect_ratio = "1:1"
                                elif formato_capa == "Vertical (9:16)": aspect_ratio = "9:16"
                                elif formato_capa == "Horizontal (16:9)": aspect_ratio = "16:9"
                                    
                                if "image_prompt" in meta and aspect_ratio:
                                    cover_ia_path = os.path.join(m_data['pasta'], "cover_ia.jpg")
                                    if not os.path.exists(cover_ia_path):
                                        self.tree_musicas.set(item_id, "status", f"Gerando Capa {aspect_ratio}...")
                                        gemini.generate_image(meta["image_prompt"], output_path=cover_ia_path, aspect_ratio=aspect_ratio)
                                    if os.path.exists(cover_ia_path):
                                        m_data['cover'] = cover_ia_path
                        except: pass
                
                # 2. Resolução do Template
                self.tree_musicas.set(item_id, "status", "Renderizando...")
                perfis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis_templates")
                
                chosen_template = template_file
                if chosen_template == "Aleatório (Auto)":
                    all_temps = [f for f in os.listdir(perfis_dir) if f.endswith('.json')]
                    if all_temps:
                        chosen_template = random.choice(all_temps)
                    else:
                        raise Exception("Nenhum template encontrado para modo aleatório.")
                        
                final_template_path = os.path.join(perfis_dir, chosen_template)
                
                # 3. Gera o vídeo
                engine.generate_music_video(
                    audio_path=m_data['audio'],
                    bg_dir=bg_dir,
                    song_name=song_name,
                    output_path=out_path,
                    template_path=final_template_path,
                    cover_path=m_data.get('cover'),
                    callback=lambda msg: print(msg)
                )
                
                self.tree_musicas.set(item_id, "status", "Concluído")
            except Exception as e:
                print(f"Erro ao processar {m_data['nome']}: {e}")
                self.tree_musicas.set(item_id, "status", "Erro")
                
        messagebox.showinfo("Sucesso", f"Geração em Lote Concluída!")

    def _construir_compilador(self):
        # Frame Principal Superior
        frame_top = ctk.CTkLabelFrame(self.frame_compilador, text="1. Fonte dos Arquivos")
        frame_top.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(frame_top, text="Pasta com Clipes Gerados:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.var_pasta_clipes = tk.StringVar()
        ctk.CTkEntry(frame_top, textvariable=self.var_pasta_clipes, width=60).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(frame_top, text="Procurar Pasta", command=lambda: self.var_pasta_clipes.set(filedialog.askdirectory())).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame Duração e Opções
        frame_opcoes = ctk.CTkLabelFrame(self.frame_compilador, text="2. Configuração do Compilado / Live")
        frame_opcoes.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(frame_opcoes, text="Duração do Vídeo Final:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.var_duracao = tk.IntVar(value=60)
        
        frame_botoes = ctk.CTkFrame(frame_opcoes)
        frame_botoes.grid(row=0, column=1, sticky='w')
        
        def set_duracao(val):
            self.var_duracao.set(val)
            
        ctk.CTkButton(frame_botoes, text="30 Min", command=lambda: set_duracao(30)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(frame_botoes, text="1 Hora", command=lambda: set_duracao(60)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(frame_botoes, text="2 Horas", command=lambda: set_duracao(120)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(frame_botoes, text="4 Horas", command=lambda: set_duracao(240)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(frame_botoes, text="12 Horas", command=lambda: set_duracao(720)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(frame_botoes, text="24 Horas", command=lambda: set_duracao(1440)).pack(side=tk.LEFT, padx=2)
        
        ctk.CTkLabel(frame_opcoes, text="Ou digite (em minutos):").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        ctk.CTkEntry(frame_opcoes, textvariable=self.var_duracao, width=150).grid(row=1, column=1, sticky='w')
        
        # Informativo
        ctk.CTkLabel(frame_opcoes, text="ℹ️ O sistema unificará os vídeos aleatoriamente até atingir a duração desejada.\nO vídeo final será exportado mantendo a qualidade original sem re-encodar, garantindo um arquivo leve e rápido.", text_color="gray").grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='w')
        
        # Ações
        frame_acoes = ctk.CTkFrame(self.frame_compilador)
        frame_acoes.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkButton(frame_acoes, text="🚀 Iniciar Compilação Profunda (Auto Loop)", command=self._iniciar_compilacao_subpastas).pack(side=tk.RIGHT, padx=5, pady=10, ipadx=10, ipady=5)

        
    def _iniciar_compilacao_subpastas(self):
        root_dir = self.var_pasta_clipes.get()
        if not root_dir or not os.path.exists(root_dir):
            messagebox.showerror("Erro", "Selecione a pasta raiz onde as subpastas estão.")
            return
            
        duracao_min = self.var_duracao.get()
        if duracao_min <= 0:
            messagebox.showerror("Erro", "A duração deve ser maior que 0.")
            return
            
        threading.Thread(target=self._worker_compilar_subpastas, args=(root_dir, duracao_min), daemon=True).start()

    def _worker_compilar_subpastas(self, root_dir, duracao_min):
        engine = MusicVideoEngine(self.config_manager.workspace_dir)
        
        # Encontra todos os mp4 nas subpastas, ignorando compilados anteriores
        videos = []
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.mp4') and not file.startswith('Compilado_'):
                    videos.append(os.path.join(root, file))
                    
        if not videos:
            messagebox.showerror("Erro", "Nenhum .mp4 encontrado nas subpastas.")
            return
            
        # Estimativa simples: se cada musica tem ~3 min, para bater duracao_min precisamos de N loops
        # Para ser mais robusto, calculamos a duracao real acumulada
        total_desejado_sec = duracao_min * 60
        total_acumulado = 0
        lista_final = []
        
        print("Montando grade de compilação...")
        while total_acumulado < total_desejado_sec:
            vid = random.choice(videos)
            lista_final.append(vid)
            # Para não demorar fazendo ffprobe em todos repetidamente, assumimos ~180s ou pegamos do arquivo real
            # Para otimizar, o ideal é ter um dicionario de durações
            dur = engine.get_audio_duration(vid)
            if dur <= 0: dur = 180 
            total_acumulado += dur
            
        out_path = os.path.join(root_dir, f"Compilado_{duracao_min}Min.mp4")
        
        try:
            engine.concat_videos(lista_final, out_path, callback=lambda msg: print(msg))
            messagebox.showinfo("Sucesso", f"Compilação de {duracao_min} minutos concluída!\nSalvo em: {out_path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
