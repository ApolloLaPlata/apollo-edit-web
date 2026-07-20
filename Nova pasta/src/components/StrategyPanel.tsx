import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, AlertCircle, Loader2, Plus, Trash2, Youtube, Lightbulb, ArrowRight, RefreshCw, Zap } from 'lucide-react';
import { executeWithRetry } from '../lib/gemini';
import { Type } from '@google/genai';
import { toast } from './Toast';

interface ChannelProfile {
  id: string;
  name: string;
  description: string;
  files: { name: string; content: string }[];
  competitors?: string[];
}

interface StrategicIdea {
  title: string;
  whyNow: string;
  angle: string;
  urgency: 'Alta' | 'Média' | 'Baixa';
  competitorContext: string;
}

export function StrategyPanel() {
  const [profiles, setProfiles] = useState<ChannelProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string>('');
  const [newCompetitor, setNewCompetitor] = useState('');
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [ideas, setIdeas] = useState<StrategicIdea[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = () => {
    const saved = localStorage.getItem('channel_profiles');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setProfiles(parsed);
        if (parsed.length > 0 && !activeProfileId) {
          setActiveProfileId(parsed[0].id);
        }
      } catch (e) {
        console.error('Error parsing profiles', e);
      }
    }
  };

  const saveProfiles = (newProfiles: ChannelProfile[]) => {
    setProfiles(newProfiles);
    localStorage.setItem('channel_profiles', JSON.stringify(newProfiles));
  };

  const activeProfile = profiles.find(p => p.id === activeProfileId);

  const handleAddCompetitor = () => {
    if (!newCompetitor.trim() || !activeProfile) return;
    
    const updatedProfiles = profiles.map(p => {
      if (p.id === activeProfile.id) {
        const currentCompetitors = p.competitors || [];
        if (!currentCompetitors.includes(newCompetitor.trim())) {
          return { ...p, competitors: [...currentCompetitors, newCompetitor.trim()] };
        }
      }
      return p;
    });
    
    saveProfiles(updatedProfiles);
    setNewCompetitor('');
  };

  const handleRemoveCompetitor = (comp: string) => {
    if (!activeProfile) return;
    const updatedProfiles = profiles.map(p => {
      if (p.id === activeProfile.id) {
        return { ...p, competitors: (p.competitors || []).filter(c => c !== comp) };
      }
      return p;
    });
    saveProfiles(updatedProfiles);
  };

  const generateStrategy = async () => {
    if (!activeProfile) return;
    
    setIsAnalyzing(true);
    setError(null);
    setIdeas([]);

    try {
      const competitorsList = activeProfile.competitors && activeProfile.competitors.length > 0 
        ? activeProfile.competitors.join(', ') 
        : 'Nenhum concorrente especificado';

      const prompt = `Você é um Estrategista Chefe de Conteúdo para o YouTube.
O usuário possui o seguinte canal:
Nome: ${activeProfile.name}
Descrição/Nicho: ${activeProfile.description}
Concorrentes principais: ${competitorsList}

Sua missão é criar um plano de ataque de conteúdo URGENTE e PERSONALIZADO para este canal.
1. Use a ferramenta googleSearch para buscar as notícias mais quentes de HOJE sobre o nicho do canal (${activeProfile.description}).
2. Se houver concorrentes listados, busque o que eles publicaram recentemente ou o que está em alta no nicho deles.
3. Cruze as informações: O que está acontecendo no mundo + O que a concorrência está fazendo (ou deixando de fazer) + A identidade do canal do usuário.
4. Gere 3 ideias de vídeos ALTAMENTE ESTRATÉGICOS que o usuário deve gravar AGORA.

Para cada ideia, forneça:
- title: Um título forte e magnético.
- whyNow: Por que este vídeo deve ser feito HOJE (urgência, timing, hype).
- angle: Qual o ângulo único que o usuário deve abordar para se diferenciar da concorrência ou focar no seu público específico.
- urgency: "Alta", "Média" ou "Baixa".
- competitorContext: O que a concorrência está fazendo sobre isso e como o usuário vai superá-los.`;

      const response = await executeWithRetry((ai) => ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: prompt,
        config: {
          tools: [{ googleSearch: {} }],
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                title: { type: Type.STRING },
                whyNow: { type: Type.STRING },
                angle: { type: Type.STRING },
                urgency: { type: Type.STRING, description: "Alta, Média ou Baixa" },
                competitorContext: { type: Type.STRING }
              },
              required: ['title', 'whyNow', 'angle', 'urgency', 'competitorContext']
            }
          }
        }
      }));

      const text = response.text;
      if (!text) throw new Error('Resposta vazia da IA');
      
      const generatedIdeas = JSON.parse(text) as StrategicIdea[];
      setIdeas(generatedIdeas);

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Erro ao gerar estratégia. Tente novamente.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 flex items-center gap-2">
            <Target className="text-indigo-600" />
            Estratégia do Canal
          </h2>
          <p className="text-zinc-500 mt-1">
            Inteligência competitiva e pautas urgentes personalizadas para o seu canal.
          </p>
        </div>
      </div>

      {profiles.length === 0 ? (
        <div className="bg-white rounded-xl border border-zinc-200 p-8 text-center">
          <Target size={48} className="mx-auto text-zinc-300 mb-4" />
          <h3 className="text-lg font-semibold text-zinc-900 mb-2">Nenhum Canal Cadastrado</h3>
          <p className="text-zinc-500 mb-6 max-w-md mx-auto">
            Para receber pautas estratégicas, você precisa primeiro cadastrar o perfil do seu canal.
          </p>
          <p className="text-sm text-zinc-400">
            Vá até a aba "Roteiros" e crie um novo Perfil de Canal.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna Esquerda: Configuração do Canal */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
              <h3 className="font-semibold text-zinc-900 flex items-center gap-2 mb-4">
                <Youtube size={18} className="text-red-500" />
                Selecione o Canal
              </h3>
              
              <select
                value={activeProfileId}
                onChange={(e) => setActiveProfileId(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {profiles.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>

              {activeProfile && (
                <div className="mt-4 p-3 bg-zinc-50 rounded-lg text-sm text-zinc-600 border border-zinc-100">
                  <p className="font-medium text-zinc-900 mb-1">Nicho / Descrição:</p>
                  <p className="line-clamp-3">{activeProfile.description || 'Sem descrição.'}</p>
                </div>
              )}
            </div>

            {activeProfile && (
              <div className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm">
                <h3 className="font-semibold text-zinc-900 flex items-center gap-2 mb-4">
                  <TrendingUp size={18} className="text-indigo-600" />
                  Mapeamento da Concorrência
                </h3>
                <p className="text-xs text-zinc-500 mb-4">
                  Adicione os nomes ou links dos seus principais concorrentes para a IA monitorar o que eles estão fazendo.
                </p>

                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={newCompetitor}
                    onChange={(e) => setNewCompetitor(e.target.value)}
                    placeholder="Ex: Canal do Fulano"
                    className="flex-1 px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    onKeyDown={(e) => e.key === 'Enter' && handleAddCompetitor()}
                  />
                  <button
                    onClick={handleAddCompetitor}
                    disabled={!newCompetitor.trim()}
                    className="px-3 py-2 bg-zinc-900 text-white rounded-lg hover:bg-zinc-800 disabled:opacity-50 transition-colors"
                  >
                    <Plus size={18} />
                  </button>
                </div>

                <ul className="space-y-2">
                  {(activeProfile.competitors || []).map((comp, i) => (
                    <li key={i} className="flex items-center justify-between p-2 bg-zinc-50 rounded-md border border-zinc-100 text-sm">
                      <span className="text-zinc-700 truncate">{comp}</span>
                      <button
                        onClick={() => handleRemoveCompetitor(comp)}
                        className="text-zinc-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </li>
                  ))}
                  {(!activeProfile.competitors || activeProfile.competitors.length === 0) && (
                    <li className="text-sm text-zinc-400 italic text-center py-2">
                      Nenhum concorrente adicionado.
                    </li>
                  )}
                </ul>
              </div>
            )}
          </div>

          {/* Coluna Direita: Pautas e Estratégia */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-gradient-to-br from-indigo-900 to-indigo-800 rounded-xl p-6 text-white shadow-md relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Target size={120} />
              </div>
              <div className="relative z-10">
                <h3 className="text-xl font-bold mb-2">Radar Estratégico</h3>
                <p className="text-indigo-200 text-sm mb-6 max-w-lg">
                  Nossa IA cruza os dados do seu canal, as notícias de hoje e o movimento da sua concorrência para entregar os vídeos que você precisa gravar agora.
                </p>
                <button
                  onClick={generateStrategy}
                  disabled={isAnalyzing || !activeProfile}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-indigo-900 font-semibold rounded-lg hover:bg-indigo-50 transition-colors disabled:opacity-70"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Analisando Mercado...
                    </>
                  ) : (
                    <>
                      <Zap size={18} className="text-indigo-600" />
                      Gerar Pautas Urgentes
                    </>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-start gap-3">
                <AlertCircle size={20} className="shrink-0 mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {ideas.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-bold text-zinc-900 flex items-center gap-2">
                  <Lightbulb className="text-amber-500" />
                  Oportunidades de Vídeo Encontradas
                </h3>
                
                <div className="grid gap-4">
                  {ideas.map((idea, index) => (
                    <div key={index} className="bg-white rounded-xl border border-zinc-200 p-5 shadow-sm hover:border-indigo-300 transition-colors">
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <h4 className="font-bold text-lg text-zinc-900 leading-tight">
                          {idea.title}
                        </h4>
                        <span className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                          idea.urgency === 'Alta' ? 'bg-red-100 text-red-700' :
                          idea.urgency === 'Média' ? 'bg-amber-100 text-amber-700' :
                          'bg-emerald-100 text-emerald-700'
                        }`}>
                          Urgência {idea.urgency}
                        </span>
                      </div>
                      
                      <div className="space-y-3 text-sm">
                        <div className="flex items-start gap-2">
                          <AlertCircle size={16} className="text-indigo-600 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-semibold text-zinc-900 block">Por que fazer agora?</span>
                            <span className="text-zinc-600">{idea.whyNow}</span>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-2">
                          <Target size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-semibold text-zinc-900 block">Seu Ângulo Único:</span>
                            <span className="text-zinc-600">{idea.angle}</span>
                          </div>
                        </div>

                        <div className="flex items-start gap-2 bg-zinc-50 p-3 rounded-lg border border-zinc-100 mt-2">
                          <Youtube size={16} className="text-red-500 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Contexto da Concorrência</span>
                            <span className="text-zinc-600 text-xs">{idea.competitorContext}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-4 pt-4 border-t border-zinc-100 flex justify-end">
                        <button 
                          className="flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
                          onClick={() => {
                            // In a real app, this would navigate to the Scripts tab and pre-fill the topic
                            toast.info('Para criar o roteiro, vá até a aba "Roteiros" e cole o título sugerido.');
                          }}
                        >
                          Criar Roteiro para este Vídeo <ArrowRight size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
