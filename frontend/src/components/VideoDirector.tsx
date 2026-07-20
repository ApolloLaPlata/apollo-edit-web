import React, { useState, useRef, useEffect } from 'react';
import { GenerationSettings } from '../types';
import toast from 'react-hot-toast';
import { Play, Image as ImageIcon, Clapperboard, Trash2, Check, Video, AlertTriangle } from 'lucide-react';
import { checkComfyConnection, uploadImageToComfyUI, injectImageIntoWorkflow, injectPromptIntoWorkflow, queuePrompt, waitForPromptCompletion } from '../services/comfyService';

interface VideoDirectorProps {
  settings: GenerationSettings;
}

interface Cue {
  id: string;
  type: 'CORTA' | 'CONTINUA';
  text: string;
  originalText: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  videoUrl?: string;
  thumbnailUrl?: string; // Tumb do frame que alimentou
}

export const extractLastFrame = async (videoUrl: string): Promise<string> => {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.crossOrigin = "anonymous";
        video.src = videoUrl;
        video.muted = true;
        
        video.addEventListener('loadeddata', () => {
            // Ir para frame quase final
            video.currentTime = Math.max(0, video.duration - 0.1);
        });

        video.addEventListener('seeked', () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                resolve(canvas.toDataURL('image/png'));
            } else {
                reject(new Error("Erro contexto canvas"));
            }
        });

        video.addEventListener('error', (e) => reject(e));
        
        video.load();
    });
};

const VideoDirector: React.FC<VideoDirectorProps> = ({ settings }) => {
    const [scriptInput, setScriptInput] = useState<string>("[CORTA] o macaco abre um sorriso e comprimenta\n[CONTINUA] o macaco pega uma grande banana e come\n[CONTINUA] o macaco entra no carro\n[CORTA] o macacao da um sorriso e da uma joinha\n[CONTINUA] o macaco liga o carro e anda\n[CORTA] o carro sai rodando\n[CONTINUA] o carro começa a corre muito rapido\n[CONTINUA] o carro bate no poste com força e fica todo amaçado");
    const [cues, setCues] = useState<Cue[]>([]);
    const [images, setImages] = useState<{id: string, base64: string}[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Parse logic
    useEffect(() => {
        const lines = scriptInput.split('\n').filter(l => l.trim());
        const parsed = lines.map(l => {
            const isCut = l.toUpperCase().includes('[CORTA]');
            return {
                id: crypto.randomUUID(),
                type: isCut ? 'CORTA' : 'CONTINUA' as ('CORTA' | 'CONTINUA'),
                originalText: l,
                text: l.replace(/.*?(CORTA|CONTINUA)\]/i, '').trim(),
                status: 'pending'
            } as Cue;
        });
        setCues(parsed);
    }, [scriptInput]);

    const totalCorta = cues.filter(c => c.type === 'CORTA').length;

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImages(prev => [...prev, { id: crypto.randomUUID(), base64: reader.result as string }]);
            };
            if(file) reader.readAsDataURL(file);
        });
        if (e.target) e.target.value = '';
    };

    const removeImage = (id: string) => setImages(prev => prev.filter(i => i.id !== id));

    const executeDirector = async () => {
        if (!settings.comfyUrl || !settings.comfyVideoWorkflow) {
            toast.error("Você precisa configurar seu ComfyUI (Aba Videos) nas Configurações.");
            return;
        }

        if (images.length < totalCorta) {
            toast.error(`Precisa de ${totalCorta} imagens de Referência (Uma para cada "CORTA"). Atualmente: ${images.length}.`);
            return;
        }

        setIsProcessing(true);
        let cortaIndex = 0;
        let lastGeneratedFrame = "";

        // Reset status
        setCues(prev => prev.map(c => ({...c, status: 'pending', videoUrl: undefined, thumbnailUrl: undefined})));

        try {
            await checkComfyConnection(settings.comfyUrl, settings.comfyApiKey);

            for (let i=0; i<cues.length; i++) {
                const cue = cues[i];
                let sourceBase64 = "";

                setCues(prev => prev.map(c => c.id === cue.id ? {...c, status: 'processing'} : c));
                toast.loading(`Gerando Cena ${i+1}/${cues.length}: ${cue.originalText}`, { id: 'dir-toast' });

                if (cue.type === 'CORTA') {
                    sourceBase64 = images[cortaIndex].base64;
                    cortaIndex++;
                } else {
                    if (!lastGeneratedFrame) {
                        throw new Error(`Falha no Continua na cena ${i+1}. Falta o quadro anterior.`);
                    }
                    sourceBase64 = lastGeneratedFrame;
                }

                // Update UI visually with what we are feeding
                setCues(prev => prev.map(c => c.id === cue.id ? {...c, thumbnailUrl: sourceBase64} : c));

                // 1. Upload Base64 to ComfyUI
                const uploadName = await uploadImageToComfyUI(settings.comfyUrl, sourceBase64, settings.comfyApiKey);

                // 2. Prepare Workflow
                let workflow = JSON.parse(settings.comfyVideoWorkflow);
                workflow = injectImageIntoWorkflow(workflow, uploadName);
                workflow = injectPromptIntoWorkflow(workflow, cue.text);

                // 3. Queue Prompt
                const promptId = await queuePrompt(settings.comfyUrl, workflow, settings.comfyApiKey);

                // 4. Wait
                const history = await waitForPromptCompletion(settings.comfyUrl, promptId, settings.comfyApiKey);

                // 5. Get outputs
                const outputs = history[promptId].outputs;
                let videoUrl = "";

                for (const nodeId in outputs) {
                    if (outputs[nodeId].gifs && outputs[nodeId].gifs.length > 0) {
                        const media = outputs[nodeId].gifs[0];
                        if (media.url) {
                            videoUrl = media.url.startsWith('http') ? media.url : `${settings.comfyUrl}${media.url}`;
                        } else {
                            const subfolder = media.subfolder ? `${media.subfolder}/` : '';
                            videoUrl = `${settings.comfyUrl}/view?filename=${encodeURIComponent(media.filename)}&type=${media.type}&subfolder=${encodeURIComponent(subfolder)}`;
                        }
                    }
                }

                if (!videoUrl) throw new Error(`Nenhum vídeo retornado pela API na cena ${i+1}`);

                setCues(prev => prev.map(c => c.id === cue.id ? {...c, status: 'completed', videoUrl} : c));

                // 6. Extraction
                toast.loading("Extraindo último frame para continuidade...", { id: 'dir-toast' });
                lastGeneratedFrame = await extractLastFrame(videoUrl);

            }
            toast.success("Direção finalizada! 🎉", { id: 'dir-toast' });

        } catch (e: any) {
            toast.error(`Erro: ${e.message}`, { id: 'dir-toast' });
            // Cleanup current processing
            setCues(prev => prev.map(c => c.status === 'processing' ? {...c, status: 'error'} : c));
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="h-full flex flex-col md:flex-row gap-4 overflow-y-auto pb-4 pr-2">
            
            {/* Esquerda: Script e Configs */}
            <div className="w-full md:w-[45%] lg:w-[35%] flex flex-col gap-4">
                <div className="bg-slate-900 rounded-xl border border-slate-700 p-6 flex-1 flex flex-col">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                        <Clapperboard className="w-5 h-5 text-indigo-400" />
                        Script do Diretor
                    </h2>

                    {!settings.comfyUrl && (
                        <div className="bg-red-900/30 border border-red-500/50 p-4 rounded-xl flex items-center gap-3 mb-4">
                            <AlertTriangle className="text-red-400 w-5 h-5 shrink-0" />
                            <p className="text-sm text-red-200">Configure o ComfyUI nas Configurações da aplicação para gerar vídeos locais ou remotos.</p>
                        </div>
                    )}

                    <div className="flex-1 flex flex-col">
                        <label className="text-sm font-bold text-slate-300 mb-2">Digite ou cole o texto no campo abaixo:</label>
                        <p className="text-xs text-slate-500 mb-2">
                            Use <strong>[CORTA]</strong> para iniciar nova cena usando as Imagens de Referências abaixo.<br/>
                            Use <strong>[CONTINUA]</strong> para pegar automaticamente o último frame do clipe anterior e dar sequência à animação.
                        </p>
                        <textarea
                            value={scriptInput}
                            onChange={(e) => setScriptInput(e.target.value)}
                            disabled={isProcessing}
                            className="w-full flex-1 min-h-[300px] bg-slate-950 border border-slate-700 rounded-lg p-3 text-slate-300 text-sm font-mono outline-none focus:border-indigo-500 resize-none whitespace-pre-wrap leading-relaxed shadow-inner"
                        />
                    </div>

                    <div className="mt-4 flex flex-col gap-2">
                        <input multiple type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={handleImageUpload} />
                        
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-bold text-slate-300">Imagens de Enredo (Ref. para CORTA)</span>
                            <span className={`text-xs px-2 py-1 rounded font-bold ${images.length < totalCorta ? 'bg-orange-900/50 text-orange-400' : 'bg-green-900/50 text-green-400'}`}>
                                {images.length}/{totalCorta} Necessárias
                            </span>
                        </div>

                        <div className="flex flex-wrap gap-2 mb-4">
                            {images.map((img, i) => (
                                <div key={img.id} className="relative w-16 h-16 rounded border border-slate-700 group overflow-hidden bg-slate-800">
                                    <img src={img.base64} className="w-full h-full object-cover" />
                                    <div className="absolute top-0 left-0 bg-black/60 px-1 py-0.5 text-[8px] font-bold">Cena {i+1}</div>
                                    <button 
                                        onClick={() => !isProcessing && removeImage(img.id)}
                                        className="absolute inset-0 bg-red-900/50 items-center justify-center hidden group-hover:flex transition-all"
                                    >
                                        <Trash2 className="w-4 h-4 text-white" />
                                    </button>
                                </div>
                            ))}
                            <button 
                                onClick={() => fileInputRef.current?.click()}
                                disabled={isProcessing}
                                className="w-16 h-16 rounded border border-dashed border-slate-600 flex flex-col items-center justify-center hover:bg-slate-800 hover:border-slate-500 text-slate-500 transition-colors"
                            >
                                <ImageIcon className="w-4 h-4 mb-1" />
                                <span className="text-[10px]">Adicionar</span>
                            </button>
                        </div>

                        <button
                            onClick={executeDirector}
                            disabled={isProcessing || !scriptInput.trim()}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-900/50"
                        >
                            {isProcessing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 fill-white" />}
                            {isProcessing ? "Gravando Cenas..." : "Iniciar GRAVAÇÃO EM CADEIA"}
                        </button>
                    </div>
                </div>
            </div>

            {/* Direita: Preview Cenas Processadas */}
            <div className="w-full md:flex-1 bg-slate-900/60 rounded-xl border border-slate-800 p-6 flex flex-col relative overflow-hidden">
                <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-slate-900/80 to-transparent pointer-events-none z-10" />

                <h3 className="text-xl font-bold text-white mb-6 relative z-20 flex items-center gap-2">
                    <Video className="w-5 h-5 text-indigo-400" /> Cenas (Filme)
                </h3>

                <div className="flex-1 overflow-y-auto space-y-4 pr-2 relative z-20">
                    {cues.length === 0 && (
                        <div className="text-center text-slate-600 italic py-10">
                            Nenhum prompt carregado
                        </div>
                    )}

                    {cues.map((cue, i) => (
                        <div 
                            key={cue.id}
                            className={`p-4 rounded-xl border bg-slate-950 flex flex-col gap-3 transition-all ${
                                cue.status === 'processing' ? 'border-indigo-500 shadow-lg shadow-indigo-500/20' : 
                                cue.status === 'completed' ? 'border-green-500/50' : 
                                cue.status === 'error' ? 'border-red-500/50' : 'border-slate-800'
                            }`}
                        >
                            <div className="flex justify-between items-start">
                                <div className="flex items-center gap-2">
                                    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${cue.type === 'CORTA' ? 'bg-orange-900 text-orange-200' : 'bg-blue-900 text-blue-200'}`}>
                                        {cue.type}
                                    </span>
                                    <span className="text-slate-500 text-xs font-mono">Cena {i+1}</span>
                                </div>
                                
                                {cue.status === 'pending' && <div className="w-2 h-2 rounded-full bg-slate-700" />}
                                {cue.status === 'processing' && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
                                {cue.status === 'completed' && <Check className="w-4 h-4 text-green-400" />}
                                {cue.status === 'error' && <AlertTriangle className="w-4 h-4 text-red-500" />}

                            </div>
                            
                            <p className="text-slate-300 text-sm">{cue.text}</p>

                            {(cue.thumbnailUrl || cue.videoUrl) && (
                                <div className="mt-2 flex items-center gap-4 border-t border-slate-800 pt-3">
                                    {cue.thumbnailUrl && (
                                        <div className="w-24 shrink-0 flex flex-col">
                                            <span className="text-[10px] text-slate-500 mb-1">Entrada (Frame)</span>
                                            <img src={cue.thumbnailUrl} className="w-full aspect-video object-cover rounded opacity-80" />
                                        </div>
                                    )}
                                    {cue.videoUrl && (
                                        <>
                                            <div className="text-slate-600 flex items-center justify-center"><ArrowRight className="w-4 h-4" /></div>
                                            <div className="w-48 shrink-0 flex flex-col">
                                                <span className="text-[10px] text-green-500 mb-1">Vídeo Gerado</span>
                                                <video src={cue.videoUrl} autoPlay loop muted playsInline className="w-full aspect-video rounded border border-slate-700 object-cover bg-black" />
                                            </div>
                                        </>
                                    )}
                                </div>
                            )}

                        </div>
                    ))}
                </div>
            </div>

        </div>
    );
};

export default VideoDirector;
