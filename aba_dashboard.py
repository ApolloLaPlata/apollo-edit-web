"""
[PARTE 11] Dashboard de Produção.
Lê o historico_renders.json (banco de dados) e exibe estatísticas de produção,
isolando por canal (Aba Local), mostrando uma visão geral (Aba Global) e Custos (Aba IA).
"""
import tkinter as tk
from tkinter import ttk
import json
import os
import datetime
import threading
import collections
import math
import queue


import customtkinter as ctk

class CTkLabelFrame(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        if text:
            self.lbl = ctk.CTkLabel(self, text=text, font=("Segoe UI", 13, "bold"), text_color="#0A84FF")
            self.lbl.place(x=15, y=5)

ctk.CTkLabelFrame = CTkLabelFrame


class AbaDashboard(ctk.CTkFrame):
    """Dashboard de Produção — mostra histórico, KPIs, ritmo e custos."""

    def __init__(self, parent, config_manager=None, app_ref=None):
        super().__init__(parent, fg_color="transparent")
        self.config_manager = config_manager
        self.app_ref        = app_ref
        
        self.historico_local = []
        self.historico_global = []
        
        self.ui_queue = queue.Queue()
        self._build_ui()
        self.after(500, self._atualizar)
        # Auto-refresh a cada 60s
        self._agendar_refresh()
        self._poll_queue()

    def _poll_queue(self):
        while not self.ui_queue.empty():
            try:
                func = self.ui_queue.get_nowait()
                func()
            except queue.Empty:
                break
        self.after(100, self._poll_queue)

    # ─────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────

    def _build_ui(self):
        main = ctk.CTkFrame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        hdr = ctk.CTkFrame(main)
        hdr.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(hdr, text="📊 DEXboard de Produção",
                  font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT)
                  
        self.btn_refresh = ctk.CTkButton(hdr, text="🔄 Atualizar", command=self._atualizar)
        self.btn_refresh.pack(side=tk.RIGHT)
        self.lbl_atualizado = ctk.CTkLabel(hdr, text="", font=("Segoe UI", 9))
        self.lbl_atualizado.pack(side=tk.RIGHT, padx=20)

        # ── Alerta Rápido ─────────────────────────────────────
        self.frame_alerta = ctk.CTkFrame(main, fg_color="transparent")
        self.lbl_alerta = ctk.CTkLabel(self.frame_alerta, text="",
                                   font=("Segoe UI", 10, "bold"))
        # pack_forget by default, só aparece se houver erro recente
        
        # Notebook principal para dividir as Visões
        self.notebook = ctk.CTkTabview(main)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.aba_local = self.notebook.add("⭐ Canal Atual")
        self.aba_global = self.notebook.add("🌍 Visão Global")
        self.aba_custos = self.notebook.add("💰 Custos & IA")

        self._build_aba_local(self.aba_local)
        self._build_aba_global(self.aba_global)
        self._build_aba_custos(self.aba_custos)

    def _build_aba_local(self, parent):
        # ── Sinais Vitais (Saúde do Sistema) ──────────────────
        self.lf_health = ctk.CTkLabelFrame(parent, text=" 🩺 Saúde do Sistema (Tempo Real) ")
        self.lf_health.pack(fill=tk.X, pady=6, padx=8)
        
        self._health_frame = ctk.CTkFrame(self.lf_health)
        self._health_frame.pack(fill=tk.X, padx=20, pady=8)

        self._health_kpis = {}
        health_defs = [
            ("ffmpeg",  "🎬 Motor (FFmpeg)"),
            ("disk",    "💾 Espaço Livre"),
            ("queue",   "⚡ Fila (Local)"),
            ("profiles","🎨 Canais Totais"),
        ]
        
        for col, (key, label) in enumerate(health_defs):
            frame = ctk.CTkFrame(self._health_frame)
            frame.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            self._health_frame.columnconfigure(col, weight=1)
            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 9)).pack(pady=(8, 2))
            val_lbl = ctk.CTkLabel(frame, text="—", font=("Segoe UI", 12, "bold"))
            val_lbl.pack(pady=(0, 8))
            self._health_kpis[key] = val_lbl

        # ── KPI Cards ─────────────────────────────────────────
        lf_kpi = ctk.CTkLabelFrame(parent, text=" 📈 Indicadores do Canal Atual ")
        lf_kpi.pack(fill=tk.X, pady=6, padx=8)

        self._kpi_frame = ctk.CTkFrame(lf_kpi)
        self._kpi_frame.pack(fill=tk.X, padx=20, pady=8)

        self._kpis_local = {}
        kpi_defs = [
            ("total",      "🎬 Total Renders"),
            ("sucesso",    "✅ Sucesso"),
            ("semana",     "📆 Esta Semana"),
            ("taxa",       "🎯 Taxa Sucesso"),
        ]
        for col, (key, label) in enumerate(kpi_defs):
            frame = ctk.CTkFrame(self._kpi_frame)
            frame.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            self._kpi_frame.columnconfigure(col, weight=1)

            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 9)).pack(pady=(8, 2))
            val_lbl = ctk.CTkLabel(frame, text="—", font=("Segoe UI", 22, "bold"))
            val_lbl.pack(pady=(0, 8))
            self._kpis_local[key] = val_lbl

        # ── Ritmo Diário ─────────────────────
        lf_ritmo = ctk.CTkLabelFrame(parent, text=" 📅 Ritmo Diário (últimos 7 dias) ")
        lf_ritmo.pack(fill=tk.BOTH, pady=6, padx=8)

        self._canvas_ritmo_local = tk.Canvas(lf_ritmo, height=90)
        self._canvas_ritmo_local.pack(fill=tk.X, padx=8, pady=8)

        # ── Histórico Recente ─────────────────────────────────
        lf_hist = ctk.CTkLabelFrame(parent, text=" 🕓 Histórico Recente ")
        lf_hist.pack(fill=tk.BOTH, expand=True, pady=6, padx=8)

        cols_hist = ("data", "audio", "status", "saida")
        self.tree_hist_local = ttk.Treeview(lf_hist, columns=cols_hist, show="headings", height=8)
        self.tree_hist_local.heading("data",   text="Data/Hora")
        self.tree_hist_local.heading("audio",  text="Título/Áudio")
        self.tree_hist_local.heading("status", text="Status")
        self.tree_hist_local.heading("saida",  text="Pasta de Saída")
        self.tree_hist_local.column("data",   width=140, anchor=tk.CENTER)
        self.tree_hist_local.column("audio",  width=250)
        self.tree_hist_local.column("status", width=100, anchor=tk.CENTER)
        self.tree_hist_local.column("saida",  width=300)

        sb = ttk.Scrollbar(lf_hist, command=self.tree_hist_local.yview)
        self.tree_hist_local.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_hist_local.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)


    def _build_aba_global(self, parent):
        # Top KPI Frame
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self._kpis_global = {}
        for col, (key, label) in enumerate([("total", "Total de Vídeos (Todos)"), ("sucesso", "Sucessos (Globais)"), ("taxa", "Eficácia Global")]):
            frame = ctk.CTkFrame(top_frame)
            frame.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            top_frame.columnconfigure(col, weight=1)
            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 9)).pack(pady=(8, 2))
            lbl = ctk.CTkLabel(frame, text="—", font=("Segoe UI", 20, "bold"))
            lbl.pack(pady=(0, 8))
            self._kpis_global[key] = lbl
            
        # Middle Frame: Gráfico Pizza + Tabela Canais
        mid_frame = ctk.CTkFrame(parent)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Canvas Pizza
        lf_pizza = ctk.CTkLabelFrame(mid_frame, text=" 🥧 Divisão de Produção ")
        lf_pizza.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self._canvas_pizza = tk.Canvas(lf_pizza, width=250, height=250)
        self._canvas_pizza.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self._legenda_pizza = ctk.CTkFrame(lf_pizza)
        self._legenda_pizza.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Tabela Canais
        lf_canal = ctk.CTkLabelFrame(mid_frame, text=" 📺 Ranking de Canais ")
        lf_canal.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))
        
        cols_canal = ("canal", "total", "sucesso", "erros")
        self.tree_canal = ttk.Treeview(lf_canal, columns=cols_canal, show="headings", height=8)
        self.tree_canal.heading("canal",   text="Canal / Perfil")
        self.tree_canal.heading("total",   text="Total")
        self.tree_canal.heading("sucesso", text="✅ OK")
        self.tree_canal.heading("erros",   text="❌ Erros")
        self.tree_canal.column("canal",   width=180)
        self.tree_canal.column("total",   width=60,  anchor=tk.CENTER)
        self.tree_canal.column("sucesso", width=60,  anchor=tk.CENTER)
        self.tree_canal.column("erros",   width=60,  anchor=tk.CENTER)
        
        sb = ttk.Scrollbar(lf_canal, command=self.tree_canal.yview)
        self.tree_canal.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_canal.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)


    def _build_aba_custos(self, parent):
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self.lbl_custo_total = ctk.CTkLabel(top_frame, text="Gasto Estimado (Total Global): $ 0.00", font=("Segoe UI", 20, "bold"))
        self.lbl_custo_total.pack(pady=20)
        
        lf_apis = ctk.CTkLabelFrame(parent, text=" 🤖 Detalhamento de Tokens e Custos de APIs ")
        lf_apis.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        cols = ("api", "canal", "tokens", "custo_estimado")
        self.tree_custos = ttk.Treeview(lf_apis, columns=cols, show="headings", height=10)
        self.tree_custos.heading("api", text="Nome da API")
        self.tree_custos.heading("canal", text="Canal (Workspace)")
        self.tree_custos.heading("tokens", text="Tokens Utilizados (Mês Atual)")
        self.tree_custos.heading("custo_estimado", text="Custo Estimado (USD)")
        
        self.tree_custos.column("api", width=150)
        self.tree_custos.column("canal", width=150)
        self.tree_custos.column("tokens", width=150, anchor=tk.CENTER)
        self.tree_custos.column("custo_estimado", width=150, anchor=tk.CENTER)
        
        self.tree_custos.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


    # ─────────────────────────────────────────────────────────
    # LÓGICA DE DADOS
    # ─────────────────────────────────────────────────────────

    def _get_canal_ativo_id(self):
        try:
            from database_manager import db
            if self.config_manager and self.config_manager.workspace_name:
                return db.get_canal_id(self.config_manager.workspace_name)
        except:
            pass
        return None

    def _carregar_historico(self, global_view=False):
        try:
            from database_manager import db
            
            canal_id = None if global_view else self._get_canal_ativo_id()
            videos = db.buscar_videos_dashboard(canal_id=canal_id, limit=1000 if global_view else 300)
            historico = []
            for v in videos:
                historico.append({
                    "data": v.get("data_inicio") or "",
                    "audio": v.get("titulo") or "",
                    "saida": v.get("filepath") or "",
                    "status": v.get("status") or "pendente",
                    "detalhe": v.get("mensagem_erro") or "",
                    "perfil": v.get("canal_nome") or "Desconhecido"
                })
            return list(reversed(historico))
        except Exception as e:
            import logging
            logging.error(f"Erro ao ler DB no dashboard: {e}")
            return []

    def _atualizar(self):
        threading.Thread(target=self._atualizar_worker, daemon=True).start()

    def _atualizar_worker(self):
        hist_local = self._carregar_historico(global_view=False)
        hist_global = self._carregar_historico(global_view=True)
        
        try:
            from database_manager import db
            # Puxamos estatísticas globalmente iterando sobre canais conhecidos se preciso,
            # Ou buscar_estatisticas_api já faz isso se não passarmos canal_id
            estatisticas = db.buscar_estatisticas_api() 
        except:
            estatisticas = {}
            
        self._verificar_saude(hist_local)
        self.ui_queue.put(lambda: self._renderizar_dados(hist_local, hist_global, estatisticas))
        
    def _verificar_saude(self, historico_local):
        import shutil
        import subprocess

        # FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            fs = "✅ Pronto"
        except Exception:
            fs = "❌ Não Instalado"

        # Disco
        pasta_saida = "C:/"
        if self.config_manager:
            pasta_saida = self.config_manager.get("pasta_saida_padrao") or "C:/"
            if not os.path.exists(pasta_saida):
                try: os.makedirs(pasta_saida, exist_ok=True)
                except: pasta_saida = "C:/"
        
        try:
            total, used, free = shutil.disk_usage(pasta_saida)
            gb_livres = free / (1024**3)
            ds = f"{gb_livres:.1f} GB"
        except Exception:
            ds = "⚠️ Indisponível"

        # Fila Local
        fila_count = 0
        if self.app_ref and hasattr(self.app_ref, "aba_fila_render"):
            fila = self.app_ref.aba_fila_render._fila
            fila_count = sum(1 for p in fila if p.get("status") == self.app_ref.aba_fila_render.STATUS_PENDENTE)
        qs = f"{fila_count} Pendentes"

        # Perfis
        perfis_count = 0
        if self.config_manager:
            perfis = self.config_manager.get("perfis_canal") or {}
            perfis_count = len(perfis)
        ps = f"{perfis_count} Prontos"

        # Último Alerta Local
        ultimo_erro = None
        for r in reversed(historico_local):
            if r.get("status") == "erro":
                ultimo_erro = r.get("detalhe", "Erro desconhecido.")
                break
            elif r.get("status") == "sucesso":
                break
        
        self.ui_queue.put(lambda: self._update_health_ui(fs, ds, qs, ps, ultimo_erro))
        
    def _update_health_ui(self, fs, ds, qs, ps, ultimo_erro):
        self._health_kpis["ffmpeg"].configure(text=fs)
        self._health_kpis["disk"].configure(text=ds)
        self._health_kpis["queue"].configure(text=qs)
        self._health_kpis["profiles"].configure(text=ps)
        
        if ultimo_erro:
            self.lbl_alerta.configure(text=f"⚠️ Falha no Último Render (Neste Canal): {ultimo_erro}")
            self.frame_alerta.pack(fill=tk.X, pady=(0, 6), before=self.notebook)
        else:
            self.frame_alerta.pack_forget()

    def _renderizar_dados(self, hist_local, hist_global, estatisticas):
        agora   = datetime.datetime.now()
        hoje    = agora.date()
        semana  = agora - datetime.timedelta(days=7)

        # ====== DADOS LOCAIS ======
        t_loc = len(hist_local)
        s_loc = sum(1 for r in hist_local if r.get("status") == "sucesso")
        sem_loc = sum(1 for r in hist_local if self._parse_data(r.get("data","")) >= semana)
        tx_loc = f"{(s_loc/t_loc*100):.0f}%" if t_loc else "—"

        self._kpis_local["total"].configure(text=str(t_loc))
        self._kpis_local["sucesso"].configure(text=str(s_loc))
        self._kpis_local["semana"].configure(text=str(sem_loc))
        self._kpis_local["taxa"].configure(text=tx_loc)

        self.tree_hist_local.delete(*self.tree_hist_local.get_children())
        for r in reversed(hist_local[-20:]):
            tag = "sucesso" if r.get("status") == "sucesso" else "erro"
            icone = "✅" if tag == "sucesso" else "❌"
            self.tree_hist_local.insert("", "end", values=(
                r.get("data",""), r.get("audio","")[:40], f"{icone} {r.get('status','')}", r.get("saida","")[:50]
            ))

        self._desenhar_ritmo_local(hist_local)

        # ====== DADOS GLOBAIS ======
        t_glob = len(hist_global)
        s_glob = sum(1 for r in hist_global if r.get("status") == "sucesso")
        tx_glob = f"{(s_glob/t_glob*100):.0f}%" if t_glob else "—"
        
        self._kpis_global["total"].configure(text=str(t_glob))
        self._kpis_global["sucesso"].configure(text=str(s_glob))
        self._kpis_global["taxa"].configure(text=tx_glob)

        self.tree_canal.delete(*self.tree_canal.get_children())
        canais = collections.defaultdict(lambda: {"total":0,"sucesso":0,"erros":0})
        for r in hist_global:
            canal = r.get("perfil") or "(sem perfil)"
            canais[canal]["total"] += 1
            if r.get("status") == "sucesso":
                canais[canal]["sucesso"] += 1
            else:
                canais[canal]["erros"] += 1

        for canal, d in sorted(canais.items(), key=lambda x: -x[1]["total"]):
            self.tree_canal.insert("", "end", values=(canal, d["total"], d["sucesso"], d["erros"]))
            
        self._desenhar_grafico_pizza(canais)
        
        # ====== CUSTOS & IA ======
        self.tree_custos.delete(*self.tree_custos.get_children())
        custo_total = 0.0
        
        # Simulando uma tabela global de custos se houver
        try:
            from database_manager import db
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.api_nome, c.nome as canal_nome, SUM(t.tokens_usados) as tk, SUM(t.custo_estimado) as ct 
                    FROM historico_tokens t 
                    LEFT JOIN canais c ON t.canal_id = c.id
                    GROUP BY t.api_nome, t.canal_id
                ''')
                for row in cursor.fetchall():
                    api = row['api_nome']
                    canal = row['canal_nome'] or "Desconhecido"
                    tk_usados = row['tk'] or 0
                    custo = row['ct'] or 0.0
                    custo_total += custo
                    self.tree_custos.insert("", "end", values=(api, canal, f"{tk_usados:,}", f"$ {custo:.4f}"))
        except:
            pass

        self.lbl_custo_total.configure(text=f"Gasto Estimado (Total Global): $ {custo_total:.2f}")

        ts = agora.strftime("%H:%M:%S")
        self.lbl_atualizado.configure(text=f"Atualizado às {ts}")

    def _desenhar_ritmo_local(self, historico):
        canvas = self._canvas_ritmo_local
        canvas.delete("all")
        w = canvas.winfo_width() or 600
        h = 90

        dias = []
        counts = []
        for delta in range(6, -1, -1):
            d = (datetime.datetime.now() - datetime.timedelta(days=delta)).date()
            c = sum(1 for r in historico
                    if self._parse_data(r.get("data","")).date() == d
                    and r.get("status") == "sucesso")
            dias.append(d.strftime("%d/%m"))
            counts.append(c)

        max_c = max(counts) if any(counts) else 1
        bar_w = (w - 40) // 7
        pad_x = 20

        for i, (dia, cnt) in enumerate(zip(dias, counts)):
            x0 = pad_x + i * bar_w + 4
            x1 = x0 + bar_w - 8
            bh = int((cnt / max_c) * 60) if max_c else 0
            y0 = h - 22 - bh
            y1 = h - 22

            cor = "#2ED573" if cnt > 0 else "gray"
            canvas.create_rectangle(x0, y0, x1, y1, fill=cor, outline="")
            if cnt > 0:
                canvas.create_text((x0+x1)//2, y0-4, text=str(cnt), font=("Segoe UI", 8, "bold"))
            canvas.create_text((x0+x1)//2, h-10, text=dia, font=("Segoe UI", 8))

    def _desenhar_grafico_pizza(self, canais_dict):
        canvas = self._canvas_pizza
        canvas.delete("all")
        for widget in self._legenda_pizza.winfo_children():
            widget.destroy()
            
        w = canvas.winfo_width() or 250
        h = canvas.winfo_height() or 250
        
        # Center coordinates and radius
        cx = w / 2
        cy = h / 2
        r = min(w, h) / 2.2
        
        bbox = (cx - r, cy - r, cx + r, cy + r)
        
        total_videos = sum(d["total"] for d in canais_dict.values())
        if total_videos == 0:
            canvas.create_oval(*bbox, fill="gray", outline="")
            canvas.create_text(cx, cy, text="Sem Dados", font=("Segoe UI", 10, "bold"))
            return
            
        cores = ["#FFD32A", "#1E90FF", "#9B59B6", "#00E676", "#FF4757", "#FFA502", "#7BED9F"]
        
        angulo_inicial = 0
        idx = 0
        
        for canal, dados in sorted(canais_dict.items(), key=lambda x: -x[1]["total"]):
            fatia = (dados["total"] / total_videos) * 360
            cor = cores[idx % len(cores)]
            
            if fatia > 0:
                canvas.create_arc(*bbox, start=angulo_inicial, extent=fatia, fill=cor, outline="white", width=1)
            
            # Adiciona na legenda
            lbl = ctk.CTkLabel(self._legenda_pizza, text=f"• {canal} ({dados['total']})", text_color=cor, font=("Segoe UI", 9, "bold"))
            lbl.pack(anchor="w")
            
            angulo_inicial += fatia
            idx += 1

    def _parse_data(self, data_str):
        try:
            return datetime.datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.datetime.min

    def _agendar_refresh(self):
        self.after(60000, self._auto_refresh)

    def _auto_refresh(self):
        self._atualizar()
        self._agendar_refresh()
