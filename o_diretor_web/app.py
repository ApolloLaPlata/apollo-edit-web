from flask import Flask, render_template, jsonify, request
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)

# Configurações de caminhos
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Garantir que as pastas existam
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)
(STATIC_DIR / "img").mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar-audio')
def gerar_audio():
    return render_template('gerar_audio.html')

@app.route('/gerar-video-narrador')
def gerar_video_narrador():
    return render_template('gerar_video_narrador.html')

@app.route('/montar-bloco')
def montar_bloco():
    return render_template('montar_bloco.html')

@app.route('/diretor-render')
def diretor_render():
    return render_template('diretor_render.html')

@app.route('/criador-templates')
def criador_templates():
    return render_template('criador_templates.html')

@app.route('/editor-video')
def editor_video():
    return render_template('editor_video.html')

@app.route('/transition')
def transition():
    return render_template('transition.html')

@app.route('/controle-volume')
def controle_volume():
    return render_template('controle_volume.html')

@app.route('/finalizacao-episodio')
def finalizacao_episodio():
    return render_template('finalizacao_episodio.html')

@app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

@app.route('/montagem-automatica')
def montagem_automatica():
    return render_template('montagem_automatica.html')

@app.route('/clipe-musical')
def clipe_musical():
    return render_template('clipe_musical.html')

@app.route('/producao-final')
def producao_final():
    return render_template('producao_final.html')

@app.route('/legendas')
def legendas():
    return render_template('legendas.html')

@app.route('/podcast')
def podcast():
    return render_template('podcast.html')

@app.route('/ajustador-midia')
def ajustador_midia():
    return render_template('ajustador_midia.html')

@app.route('/dublagem-rvc')
def dublagem_rvc():
    return render_template('dublagem_rvc.html')

@app.route('/configuracoes')
def configuracoes():
    return render_template('configuracoes.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "message": "O Diretor Web está pronto!"})

@app.route('/api/browse_file')
def browse_file():
    # Esconde a janela principal do Tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Força a janela para o topo
    
    file_type = request.args.get('type', 'all')
    if file_type == 'media':
        filetypes = [("Arquivos de Mídia (Vídeo/Foto)", "*.mp4 *.mov *.avi *.jpg *.jpeg *.png *.webp *.bmp")]
    elif file_type == 'audio':
        filetypes = [("Arquivos de Áudio", "*.mp3 *.wav *.aac *.ogg")]
    else:
        filetypes = [("Todos os Arquivos", "*.*"), ("Vídeos", "*.mp4 *.mov *.avi"), ("Áudio", "*.mp3 *.wav"), ("Imagens", "*.jpg *.png *.webp")]
    
    file_path = filedialog.askopenfilename(
        title="Selecione o Arquivo",
        filetypes=filetypes
    )
    root.destroy()
    return jsonify({"path": file_path})

@app.route('/api/browse_dir')
def browse_dir():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    dir_path = filedialog.askdirectory(title="Selecione a Pasta")
    root.destroy()
    return jsonify({"path": dir_path})

from flask import send_file

@app.route('/api/serve_file')
def serve_file():
    filepath = request.args.get('path')
    if filepath and os.path.exists(filepath):
        return send_file(filepath)
    return "File not found", 404

if __name__ == '__main__':
    # Rodando na porta 5000
    app.run(debug=True, port=5000)
