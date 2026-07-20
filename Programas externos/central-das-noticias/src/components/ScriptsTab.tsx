import React, { useState, useEffect, useRef } from 'react';
import { FileText, Plus, Trash2, UploadCloud, Loader2, Copy, CheckCircle2, AlertCircle, Download, Send } from 'lucide-react';
import { generateCustomScript } from '../lib/gemini';
import ReactMarkdown from 'react-markdown';
import { toast } from './Toast';

interface ChannelProfile {
  id: string;
  name: string;
  description: string;
  files: { name: string; content: string }[];
}

export function ScriptsTab() {
  const [profiles, setProfiles] = useState<ChannelProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string>('');
  
  // Profile Creation State
  const [isCreatingProfile, setIsCreatingProfile] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileDesc, setNewProfileDesc] = useState('');
  const [newProfileFiles, setNewProfileFiles] = useState<{ name: string; content: string }[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Script Generation State
  const [topic, setTopic] = useState('');
  const [modality, setModality] = useState('longo');
  const [tone, setTone] = useState('perfil'); // Default to profile's tone
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedScript, setGeneratedScript] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('channel_profiles');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setProfiles(parsed);
        if (parsed.length > 0) {
          setActiveProfileId(parsed[0].id);
        }
      } catch (e) {
        console.error('Error parsing profiles', e);
      }
    }
  }, []);

  const saveProfiles = (newProfiles: ChannelProfile[]) => {
    setProfiles(newProfiles);
    localStorage.setItem('channel_profiles', JSON.stringify(newProfiles));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const newFiles: { name: string; content: string }[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const text = await file.text();
      newFiles.push({ name: file.name, content: text });
    }

    setNewProfileFiles(prev => [...prev, ...newFiles]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleCreateProfile = () => {
    if (!newProfileName.trim()) {
      toast.error('Dê um nome ao perfil.');
      return;
    }

    const newProfile: ChannelProfile = {
      id: Date.now().toString(),
      name: newProfileName,
      description: newProfileDesc,
      files: newProfileFiles,
    };

    const updated = [...profiles, newProfile];
    saveProfiles(updated);
    setActiveProfileId(newProfile.id);
    
    // Reset form
    setIsCreatingProfile(false);
    setNewProfileName('');
    setNewProfileDesc('');
    setNewProfileFiles([]);
  };

  const handleDeleteProfile = (id: string) => {
    if (confirm('Tem certeza que deseja excluir este perfil?')) {
      const updated = profiles.filter(p => p.id !== id);
      saveProfiles(updated);
      if (activeProfileId === id) {
        setActiveProfileId(updated.length > 0 ? updated[0].id : '');
      }
    }
  };

  const removeNewFile = (index: number) => {
    setNewProfileFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error('Por favor, insira o tema ou texto base para o roteiro.');
      return;
    }

    const activeProfile = profiles.find(p => p.id === activeProfileId);
    
    setIsGenerating(true);
    setGeneratedScript('');
    
    try {
      const script = await generateCustomScript(topic, modality, tone, activeProfile);
      setGeneratedScript(script);
      
      // Save to history (limit to 50)
      const savedScripts = JSON.parse(localStorage.getItem('scripts_history') || '[]');
      const newSavedScript = {
        id: Date.now().toString(),
        title: topic.substring(0, 50) + '...',
        content: script,
        date: new Date().toISOString(),
        type: modality
      };
      try {
        localStorage.setItem('scripts_history', JSON.stringify([newSavedScript, ...savedScripts].slice(0, 50)));
      } catch (e) {
        console.warn('Could not save to history, localStorage might be full');
      }
      
    } catch (error: any) {
      toast.error(error.message || 'Erro ao gerar roteiro.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedScript).then(() => {
      setCopied(true);
      toast.success('Roteiro copiado!');
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownloadTXT = () => {
    const element = document.createElement("a");
    const file = new Blob([generatedScript], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `roteiro_${Date.now()}.txt`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
    document.body.removeChild(element);
    toast.success('Download iniciado!');
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2">
            <FileText className="text-indigo-600" />
            Central de Roteiros
          </h2>
          <p className="text-zinc-400 mt-1">Crie roteiros personalizados com a identidade do seu canal.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Generator */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-zinc-900 rounded-xl shadow-sm border border-zinc-800 p-6">
            <h3 className="text-lg font-semibold text-zinc-100 mb-4">Gerador de Roteiro</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1">Perfil do Canal</label>
                {profiles.length > 0 ? (
                  <select
                    value={activeProfileId}
                    onChange={(e) => setActiveProfileId(e.target.value)}
                    className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  >
                    <option value="">Sem perfil específico (Genérico)</option>
                    {profiles.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                ) : (
                  <div className="text-sm text-yellow-600 bg-yellow-50 p-3 rounded-lg border border-yellow-200 flex items-start gap-2">
                    <AlertCircle size={16} className="mt-0.5 shrink-0" />
                    <p>Você ainda não tem perfis cadastrados. O roteiro será gerado com um tom genérico. Crie um perfil ao lado para treinar a IA com a sua identidade.</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Modalidade do Roteiro</label>
                  <select
                    value={modality}
                    onChange={(e) => setModality(e.target.value)}
                    className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  >
                    <option value="longo">Vídeo Longo Padrão (8-12 min)</option>
                    <option value="curto">Vídeo Curto (3-5 min)</option>
                    <option value="shorts">Shorts / TikTok / Reels (até 60s)</option>
                    <option value="corte">Corte Estilo Podcast (1-3 min)</option>
                    <option value="documentario">Documentário / Ensaio de Vídeo</option>
                    <option value="noticias">Notícias / Jornalismo</option>
                    <option value="review">Review de Produto</option>
                    <option value="tutorial">Tutorial / Passo a Passo</option>
                    <option value="storytelling">Storytelling / Relato Pessoal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Tom de Voz / Estilo</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  >
                    <option value="perfil">Usar a Identidade do Perfil (Recomendado)</option>
                    <option value="sarcastico">Sarcástico / Irônico</option>
                    <option value="comedia">Humor / Comédia</option>
                    <option value="agressivo">Agressivo / Polêmico</option>
                    <option value="serio">Sério / Jornalístico</option>
                    <option value="descontraido">Descontraído / Bate-papo</option>
                    <option value="inspirador">Inspirador / Motivacional</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-sm font-medium text-zinc-700">Tema, Link ou Texto Base</label>
                  {topic.trim() && (
                    <button 
                      onClick={() => setTopic('')}
                      className="text-xs text-zinc-400 hover:text-red-500 transition-colors"
                    >
                      Limpar
                    </button>
                  )}
                </div>
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Descreva o tema, cole um LINK do YouTube, uma notícia, ou dê as instruções principais..."
                  className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[120px] resize-y"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !topic.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Gerando Roteiro...
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    Gerar Roteiro
                  </>
                )}
              </button>
            </div>
          </div>

          {generatedScript && (
            <div className="bg-zinc-900 rounded-xl shadow-sm border border-zinc-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-zinc-100">Roteiro Gerado</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleDownloadTXT}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-700 bg-zinc-800 hover:bg-zinc-200 rounded-lg transition-colors"
                  >
                    <Download size={16} />
                    Baixar TXT
                  </button>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-700 bg-zinc-800 hover:bg-zinc-200 rounded-lg transition-colors"
                  >
                    {copied ? <CheckCircle2 size={16} className="text-emerald-600" /> : <Copy size={16} />}
                    {copied ? 'Copiado!' : 'Copiar'}
                  </button>
                </div>
              </div>
              <div className="prose prose-zinc max-w-none bg-transparent p-6 rounded-lg border border-zinc-800">
                <ReactMarkdown>{generatedScript}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Profiles */}
        <div className="space-y-6">
          <div className="bg-zinc-900 rounded-xl shadow-sm border border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-zinc-100">Perfis de Canal</h3>
              {!isCreatingProfile && (
                <button
                  onClick={() => setIsCreatingProfile(true)}
                  className="p-1.5 text-indigo-600 bg-indigo-900/30 hover:bg-indigo-100 rounded-lg transition-colors"
                  title="Novo Perfil"
                >
                  <Plus size={20} />
                </button>
              )}
            </div>

            {isCreatingProfile ? (
              <div className="space-y-4 bg-transparent p-4 rounded-lg border border-zinc-800">
                <h4 className="font-medium text-zinc-100 text-sm">Novo Perfil</h4>
                
                <div>
                  <label className="block text-xs font-medium text-zinc-700 mb-1">Nome do Canal/Perfil</label>
                  <input
                    type="text"
                    value={newProfileName}
                    onChange={(e) => setNewProfileName(e.target.value)}
                    placeholder="Ex: Canal de Finanças"
                    className="w-full px-3 py-1.5 text-sm bg-zinc-900 border border-zinc-700 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-zinc-700 mb-1">Descrição (Opcional)</label>
                  <textarea
                    value={newProfileDesc}
                    onChange={(e) => setNewProfileDesc(e.target.value)}
                    placeholder="Público alvo, estilo principal..."
                    className="w-full px-3 py-1.5 text-sm bg-zinc-900 border border-zinc-700 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none h-16"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-700 mb-1">Arquivos de Treinamento (TXT, MD)</label>
                  <p className="text-xs text-zinc-400 mb-2">Faça upload de roteiros antigos, guias de estilo ou textos que representem a identidade do canal.</p>
                  
                  <input
                    type="file"
                    multiple
                    accept=".txt,.md,.csv"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full py-2 border-2 border-dashed border-zinc-700 rounded-lg text-sm text-zinc-400 hover:border-indigo-500 hover:text-indigo-600 transition-colors flex items-center justify-center gap-2"
                  >
                    <UploadCloud size={16} />
                    Selecionar Arquivos
                  </button>

                  {newProfileFiles.length > 0 && (
                    <ul className="mt-3 space-y-2">
                      {newProfileFiles.map((f, i) => (
                        <li key={i} className="flex items-center justify-between text-xs bg-zinc-900 p-2 border border-zinc-800 rounded">
                          <span className="truncate max-w-[180px]" title={f.name}>{f.name}</span>
                          <button onClick={() => removeNewFile(i)} className="text-red-500 hover:text-red-400">
                            <Trash2 size={14} />
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="flex gap-2 pt-2">
                  <button
                    onClick={handleCreateProfile}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2 rounded-md transition-colors"
                  >
                    Salvar Perfil
                  </button>
                  <button
                    onClick={() => setIsCreatingProfile(false)}
                    className="flex-1 bg-zinc-200 hover:bg-zinc-300 text-zinc-200 text-sm font-medium py-2 rounded-md transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {profiles.length === 0 ? (
                  <p className="text-sm text-zinc-400 text-center py-4">Nenhum perfil cadastrado.</p>
                ) : (
                  profiles.map(p => (
                    <div key={p.id} className={`p-3 rounded-lg border transition-colors ${activeProfileId === p.id ? 'border-indigo-500 bg-indigo-900/30' : 'border-zinc-800 bg-transparent hover:border-zinc-700'}`}>
                      <div className="flex items-start justify-between">
                        <div 
                          className="cursor-pointer flex-1"
                          onClick={() => setActiveProfileId(p.id)}
                        >
                          <h4 className="font-medium text-zinc-100 text-sm">{p.name}</h4>
                          {p.description && <p className="text-xs text-zinc-400 mt-0.5 line-clamp-2">{p.description}</p>}
                          <p className="text-xs text-indigo-600 mt-1 font-medium">{p.files.length} arquivo(s) de base</p>
                        </div>
                        <button
                          onClick={() => handleDeleteProfile(p.id)}
                          className="text-zinc-400 hover:text-red-600 p-1"
                          title="Excluir Perfil"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
