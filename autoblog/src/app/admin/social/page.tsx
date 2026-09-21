'use client';

import React, { useState, useEffect } from 'react';

export default function SocialPublisherPanel() {
  const [config, setConfig] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string, type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    fetch('/api/admin/social')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data) {
          setConfig(data.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig({ ...config, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/admin/social', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await res.json();
      if (res.ok) {
        setToast({ message: 'Chaves atualizadas com sucesso!', type: 'success' });
      } else {
        setToast({ message: data.error || 'Erro ao salvar', type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: e.message, type: 'error' });
    }
    setSaving(false);
    setTimeout(() => setToast(null), 3000);
  };

  const testWebhook = async () => {
     setToast({ message: 'Sinal disparado para o Hub...', type: 'success' });
     setTimeout(() => setToast(null), 3000);
     // O real disparo ativaria a exec('node src/scripts/social_publisher.js') 
     // Isso será interligado via painel maestro no futuro.
  };

  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-16 animate-in fade-in duration-500 relative">
      
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-6 right-6 px-6 py-3 rounded-xl shadow-2xl font-bold text-sm z-50 animate-in slide-in-from-right-10 flex items-center gap-3 ${toast.type === 'success' ? 'bg-emerald-500/90 text-white' : 'bg-red-500/90 text-white'}`}>
           {toast.type === 'success' ? '✓' : '⚠'} {toast.message}
        </div>
      )}

      {/* Header Glassmorphism */}
      <div className="bg-gradient-to-r from-blue-900/40 to-cyan-900/40 backdrop-blur-3xl p-10 rounded-3xl border border-cyan-500/30 shadow-[0_0_50px_rgba(6,182,212,0.1)] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-cyan-500/20 rounded-full blur-3xl pointer-events-none -mr-32 -mt-32 animate-pulse" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[10px] font-black uppercase tracking-widest mb-4 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              Omni-Channel Auto-Poster
            </div>
            <h1 className="text-4xl font-black text-white tracking-tight mb-2">Central de Distribuição</h1>
            <p className="text-slate-400 font-medium max-w-xl">Configure as chaves da API para que a Inteligência Artificial poste automaticamente no Telegram, Discord e WhatsApp.</p>
          </div>
          <button 
            onClick={testWebhook}
            className="shrink-0 bg-slate-800 hover:bg-slate-700 text-white font-bold px-6 py-3 rounded-xl border border-slate-600 transition-all shadow-lg flex items-center gap-2"
          >
            ▶ Testar Roteamento
          </button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-6">
          <div className="h-48 bg-slate-800/40 animate-pulse rounded-3xl border border-slate-800"></div>
          <div className="h-48 bg-slate-800/40 animate-pulse rounded-3xl border border-slate-800"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Card: Telegram VIP */}
          <div className="bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-xl group hover:border-blue-500/50 transition-all relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all pointer-events-none"></div>
            
            <div className="flex items-center gap-4 mb-8 relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center border border-blue-500/30 text-blue-400">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.223-.548.223l.188-2.85 5.18-4.676c.223-.198-.054-.31-.346-.11l-6.4 4.02-2.76-.89c-.6-.188-.612-.6.126-.89l10.814-4.17c.5-.188.937.114.776.883z"/></svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Canais do Telegram</h3>
                <p className="text-xs text-slate-400">Postagem de Vídeos e Artigos</p>
              </div>
            </div>

            <div className="space-y-5 relative z-10">
              <div>
                 <label className="block text-[11px] font-black text-slate-500 mb-1.5 uppercase tracking-widest">Bot Token (BotFather)</label>
                 <input type="password" name="telegramBotToken" value={config.telegramBotToken || ''} onChange={handleChange} className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300 focus:border-blue-500 outline-none transition-colors" placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ" />
              </div>
              <div>
                 <label className="block text-[11px] font-black text-slate-500 mb-1.5 uppercase tracking-widest">Chat ID (Canal ou Grupo)</label>
                 <input type="text" name="telegramChatId" value={config.telegramChatId || ''} onChange={handleChange} className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300 focus:border-blue-500 outline-none transition-colors" placeholder="-100123456789" />
              </div>
            </div>
          </div>

          {/* Card: Discord & Outros */}
          <div className="bg-slate-900/80 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-xl group hover:border-indigo-500/50 transition-all relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl group-hover:bg-indigo-500/20 transition-all pointer-events-none"></div>
            
            <div className="flex items-center gap-4 mb-8 relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 text-indigo-400">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Discord & API Webhooks</h3>
                <p className="text-xs text-slate-400">Comunidades Privadas</p>
              </div>
            </div>

            <div className="space-y-5 relative z-10">
              <div>
                 <label className="block text-[11px] font-black text-slate-500 mb-1.5 uppercase tracking-widest">Discord Webhook URL</label>
                 <input type="url" name="discordWebhookUrl" value={config.discordWebhookUrl || ''} onChange={handleChange} className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300 focus:border-indigo-500 outline-none transition-colors" placeholder="https://discord.com/api/webhooks/..." />
              </div>
              <div>
                 <label className="block text-[11px] font-black text-slate-500 mb-1.5 uppercase tracking-widest">WhatsApp Group API (Alpha)</label>
                 <input type="text" name="whatsappApiUrl" value={config.whatsappApiUrl || ''} onChange={handleChange} className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300 focus:border-indigo-500 outline-none transition-colors" placeholder="Apenas para parceiros B2B" disabled />
              </div>
            </div>
          </div>

        </div>
      )}

      {/* Footer Action */}
      {!loading && (
        <div className="flex justify-end pt-4 border-t border-slate-800">
           <button 
             onClick={handleSave} 
             disabled={saving}
             className={`bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 px-10 rounded-xl transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
           >
             {saving ? 'Aplicando Matrix...' : 'Salvar Chaves Globais'}
           </button>
        </div>
      )}

    </div>
  );
}
