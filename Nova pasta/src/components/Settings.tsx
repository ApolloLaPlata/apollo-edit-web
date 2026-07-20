import React, { useState, useEffect } from 'react';
import { Key, Save, CheckCircle2, AlertCircle, Twitter, Youtube, Instagram, Facebook, Video, Settings as SettingsIcon, Globe, Shield, Bot, Loader2 } from 'lucide-react';

export function Settings() {
  const [apiKeys, setApiKeys] = useState({
    grok: localStorage.getItem('api_key_grok') || '',
    openai: localStorage.getItem('api_key_openai') || '',
    gemini: localStorage.getItem('api_key_gemini') || '',
    openrouter: localStorage.getItem('api_key_openrouter') || '',
    apify: localStorage.getItem('api_key_apify') || 'apify_api_qjMUnOJLzF6v6YREHAiPboPpuQKHBL4rnr8o',
    twitter: localStorage.getItem('api_key_twitter') || '',
    youtube: localStorage.getItem('api_key_youtube') || '',
    instagram: localStorage.getItem('api_key_instagram') || '',
    facebook: localStorage.getItem('api_key_facebook') || '',
    tiktok: localStorage.getItem('api_key_tiktok') || '',
    kwai: localStorage.getItem('api_key_kwai') || '',
    pixabay: localStorage.getItem('api_key_pixabay') || '',
    pexels: localStorage.getItem('api_key_pexels') || '',
  });

  const [generalSettings, setGeneralSettings] = useState({
    theme: localStorage.getItem('setting_theme') || 'light',
    language: localStorage.getItem('setting_language') || 'pt-BR',
    autoSave: localStorage.getItem('setting_autoSave') !== 'false',
    tone: localStorage.getItem('setting_tone') || 'jornalistico',
  });

  const [savedStatus, setSavedStatus] = useState<string | null>(null);
  const [keyStatus, setKeyStatus] = useState<Record<string, { status: 'idle' | 'testing' | 'success' | 'error', message?: string }>>({});

  const handleApiChange = (key: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [key]: value }));
    // Reset status when user changes the key
    if (keyStatus[key]) {
      setKeyStatus(prev => ({ ...prev, [key]: { status: 'idle' } }));
    }
  };

  const testApiKey = async (service: string, key: string) => {
    if (!key.trim()) {
      setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'A chave não pode estar vazia' } }));
      return;
    }

    setKeyStatus(prev => ({ ...prev, [service]: { status: 'testing' } }));

    try {
      let response;
      switch (service) {
        case 'pixabay':
          response = await fetch(`https://pixabay.com/api/?key=${key}&q=test&per_page=3`);
          if (response.ok) {
            const data = await response.json();
            // Pixabay returns rate limit headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
            const remaining = response.headers.get('X-RateLimit-Remaining');
            const limitMsg = remaining ? ` (Restam ${remaining} requisições)` : '';
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: `Conectado com sucesso!${limitMsg}` } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida ou limite excedido' } }));
          }
          break;
        case 'pexels':
          response = await fetch(`https://api.pexels.com/v1/search?query=test&per_page=1`, {
            headers: { Authorization: key }
          });
          if (response.ok) {
            const remaining = response.headers.get('X-Ratelimit-Remaining');
            const limitMsg = remaining ? ` (Restam ${remaining} requisições)` : '';
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: `Conectado com sucesso!${limitMsg}` } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'grok':
          response = await fetch(`/api/grok/models`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ apiKey: key })
          });
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'openai':
          response = await fetch(`https://api.openai.com/v1/models`, {
            headers: { Authorization: `Bearer ${key}` }
          });
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'openrouter':
          response = await fetch(`https://openrouter.ai/api/v1/auth/key`, {
            headers: { Authorization: `Bearer ${key}` }
          });
          if (response.ok) {
            const data = await response.json();
            const limitMsg = data.data?.limit ? ` (Limite: $${data.data.limit})` : '';
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: `Conectado com sucesso!${limitMsg}` } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'apify':
          response = await fetch(`https://api.apify.com/v2/users/me?token=${key}`);
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso ao Apify!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave Apify inválida' } }));
          }
          break;
        case 'gemini':
          const keys = key.split('\n').map(k => k.trim()).filter(k => k.length > 0);
          if (keys.length === 0) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Nenhuma chave fornecida' } }));
            break;
          }
          
          let validCount = 0;
          let invalidLines: number[] = [];
          let lastErrorMessage = '';
          
          for (let i = 0; i < keys.length; i++) {
            try {
              const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${keys[i]}`);
              if (res.ok) {
                validCount++;
              } else {
                const errorData = await res.json().catch(() => ({}));
                lastErrorMessage = errorData?.error?.message || `Erro HTTP ${res.status}`;
                invalidLines.push(i + 1);
              }
            } catch (e: any) {
              lastErrorMessage = e.message || 'Erro de rede (CORS ou offline)';
              invalidLines.push(i + 1);
            }
          }
          
          if (invalidLines.length === 0) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: `${validCount} chave(s) testada(s) com sucesso!` } }));
          } else if (validCount === 0) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: `Falha: ${lastErrorMessage}` } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: `${validCount} válidas. Erro na(s) linha(s): ${invalidLines.join(', ')} (${lastErrorMessage})` } }));
          }
          break;
        case 'youtube':
          response = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&maxResults=1&key=${key}`);
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'twitter':
          response = await fetch(`https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10`, {
            headers: { Authorization: `Bearer ${key}` }
          });
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Chave inválida' } }));
          }
          break;
        case 'instagram':
          response = await fetch(`https://graph.instagram.com/me?access_token=${key}`);
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Token inválido' } }));
          }
          break;
        case 'facebook':
          response = await fetch(`https://graph.facebook.com/me?access_token=${key}`);
          if (response.ok) {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'success', message: 'Conectado com sucesso!' } }));
          } else {
            setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Token inválido' } }));
          }
          break;
        default:
          setKeyStatus(prev => ({ ...prev, [service]: { status: 'idle' } }));
      }
    } catch (error) {
      setKeyStatus(prev => ({ ...prev, [service]: { status: 'error', message: 'Erro de conexão ou CORS' } }));
    }
  };

  const renderApiInput = (id: keyof typeof apiKeys, label: string, placeholder: string, description?: string, isTextarea?: boolean, icon?: React.ReactNode) => {
    const status = keyStatus[id];
    const isTestable = ['pixabay', 'pexels', 'grok', 'openai', 'openrouter', 'gemini', 'youtube', 'twitter', 'instagram', 'facebook', 'apify'].includes(id);
    
    return (
      <div>
        <div className="flex justify-between items-center mb-1">
          <label className="flex items-center gap-2 text-sm font-medium text-zinc-700">
            {icon}
            {label}
          </label>
          {isTestable && (
            <button 
              onClick={() => testApiKey(id, apiKeys[id])}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1 px-2 py-1 rounded hover:bg-indigo-50 transition-colors"
              disabled={status?.status === 'testing'}
            >
              {status?.status === 'testing' ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <CheckCircle2 size={14} />
              )}
              Testar Chave
            </button>
          )}
        </div>
        <div className="relative">
          <Key size={16} className={`absolute left-3 ${isTextarea ? 'top-3' : 'top-1/2 -translate-y-1/2'} text-zinc-400`} />
          {isTextarea ? (
            <textarea 
              value={apiKeys[id]}
              onChange={(e) => handleApiChange(id, e.target.value)}
              placeholder={placeholder} 
              rows={3}
              className={`w-full pl-9 pr-4 py-2 bg-white border ${status?.status === 'error' ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : status?.status === 'success' ? 'border-emerald-300 focus:ring-emerald-500 focus:border-emerald-500' : 'border-zinc-200 focus:ring-indigo-500 focus:border-indigo-500'} rounded-lg focus:ring-2 outline-none transition-all resize-none`}
            />
          ) : (
            <input 
              type="password" 
              value={apiKeys[id]}
              onChange={(e) => handleApiChange(id, e.target.value)}
              placeholder={placeholder} 
              className={`w-full pl-9 pr-4 py-2 bg-white border ${status?.status === 'error' ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : status?.status === 'success' ? 'border-emerald-300 focus:ring-emerald-500 focus:border-emerald-500' : 'border-zinc-200 focus:ring-indigo-500 focus:border-indigo-500'} rounded-lg focus:ring-2 outline-none transition-all`}
            />
          )}
        </div>
        {status?.status === 'error' && (
          <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
            <AlertCircle size={12} /> {status.message}
          </p>
        )}
        {status?.status === 'success' && (
          <p className="text-xs text-emerald-600 mt-1 flex items-center gap-1">
            <CheckCircle2 size={12} /> {status.message}
          </p>
        )}
        {description && (!status || status.status === 'idle' || status.status === 'testing') && (
          <p className="text-xs text-zinc-500 mt-1">{description}</p>
        )}
      </div>
    );
  };

  const handleSettingChange = (key: string, value: string | boolean) => {
    setGeneralSettings(prev => ({ ...prev, [key]: value }));
  };

  const saveSettings = () => {
    // Save API keys
    Object.entries(apiKeys).forEach(([key, value]) => {
      localStorage.setItem(`api_key_${key}`, value);
    });

    // Save General Settings
    Object.entries(generalSettings).forEach(([key, value]) => {
      localStorage.setItem(`setting_${key}`, String(value));
    });

    setSavedStatus('Configurações salvas com sucesso!');
    setTimeout(() => setSavedStatus(null), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl font-bold text-zinc-900 flex items-center gap-2">
          <SettingsIcon className="text-indigo-600" />
          Configurações do Sistema
        </h2>
        <p className="text-zinc-500 mt-1">Gerencie suas chaves de API, integrações com redes sociais e preferências gerais.</p>
      </div>

      {savedStatus && (
        <div className="bg-emerald-50 text-emerald-700 p-4 rounded-lg flex items-center gap-2 border border-emerald-200">
          <CheckCircle2 size={20} />
          <span className="font-medium">{savedStatus}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Coluna 1: APIs de IA */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
            <h3 className="text-lg font-semibold text-zinc-900 flex items-center gap-2 mb-4">
              <Bot size={20} className="text-blue-600" />
              Modelos de IA
            </h3>
            
            <div className="space-y-4">
              {renderApiInput('grok', 'Grok API Key (xAI)', 'xoxb-...', 'Necessário para buscas avançadas no X/Twitter.')}
              {renderApiInput('openai', 'OpenAI API Key (ChatGPT)', 'sk-...')}
              {renderApiInput('openrouter', 'OpenRouter API Key', 'sk-or-v1-...', 'Acesso a modelos gratuitos e pagos (StepFun, Trinity, Liquid, etc).')}
              {renderApiInput('gemini', 'Gemini API Keys (Google)', 'AIzaSy...\nAIzaSy...\n(Uma chave por linha)', 'Cole várias chaves (uma por linha) para rotacionar e evitar limites de uso. Se vazio, usará a chave padrão do sistema.', true)}
              {renderApiInput('pixabay', 'Pixabay API Key', 'Sua chave do Pixabay...', 'Para buscar imagens e vídeos gratuitos de alta qualidade.')}
              {renderApiInput('pexels', 'Pexels API Key', 'Sua chave do Pexels...', 'Alternativa para busca de imagens e vídeos gratuitos.')}
              {renderApiInput('apify', 'Apify API Key', 'Sua chave do Apify...', 'Acesse console.apify.com para pegar sua chave (necessário para extração avançada de conteúdo em redes sociais)')}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
            <h3 className="text-lg font-semibold text-zinc-900 flex items-center gap-2 mb-4">
              <Shield size={20} className="text-zinc-600" />
              Preferências Gerais
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1">Estilo de Escrita (IA)</label>
                <select 
                  value={generalSettings.tone}
                  onChange={(e) => handleSettingChange('tone', e.target.value)}
                  className="w-full px-4 py-2 bg-white border border-zinc-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="jornalistico">Jornalístico (Sério, direto, imparcial)</option>
                  <option value="viral">Blog/Viral (Chamativo, emojis, parágrafos curtos)</option>
                  <option value="seo">Foco em SEO (Otimizado para o Google)</option>
                  <option value="resumo">Resumo Rápido (Direto ao ponto, bullet points)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1">Idioma Padrão</label>
                <select 
                  value={generalSettings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                  className="w-full px-4 py-2 bg-white border border-zinc-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="pt-BR">Português (Brasil)</option>
                  <option value="en-US">English (US)</option>
                  <option value="es-ES">Español</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1">Tema</label>
                <select 
                  value={generalSettings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                  className="w-full px-4 py-2 bg-white border border-zinc-200 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="light">Claro</option>
                  <option value="dark">Escuro (Em breve)</option>
                  <option value="system">Sistema</option>
                </select>
              </div>

              <div className="flex items-center gap-2 mt-4">
                <input 
                  type="checkbox" 
                  id="autoSave" 
                  checked={generalSettings.autoSave}
                  onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="autoSave" className="text-sm text-zinc-700">Salvar rascunhos automaticamente</label>
              </div>
            </div>
          </div>
        </div>

        {/* Coluna 2 e 3: Redes Sociais */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-zinc-900 flex items-center gap-2">
                <Globe size={20} className="text-emerald-600" />
                Integrações de Redes Sociais
              </h3>
              <span className="text-xs font-medium bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">
                Dashboard em Breve
              </span>
            </div>
            
            <p className="text-sm text-zinc-500 mb-6">
              Cadastre suas chaves de API para habilitar o monitoramento em tempo real de audiência, comentários e métricas no seu futuro Dashboard.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Twitter */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('twitter', 'X (Twitter) API', 'Bearer Token...', undefined, false, <Twitter size={18} className="text-sky-500" />)}
              </div>

              {/* YouTube */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('youtube', 'YouTube Data API v3', 'API Key...', undefined, false, <Youtube size={18} className="text-red-500" />)}
              </div>

              {/* Instagram */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('instagram', 'Instagram Graph API', 'Access Token...', undefined, false, <Instagram size={18} className="text-pink-600" />)}
              </div>

              {/* Facebook */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('facebook', 'Facebook Graph API', 'Access Token...', undefined, false, <Facebook size={18} className="text-blue-600" />)}
              </div>

              {/* TikTok */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('tiktok', 'TikTok API', 'Client Secret / Token...', undefined, false, <Video size={18} className="text-black" />)}
              </div>

              {/* Kwai */}
              <div className="p-4 border border-zinc-100 rounded-lg bg-zinc-50/50">
                {renderApiInput('kwai', 'Kwai API', 'Access Token...', undefined, false, <Video size={18} className="text-orange-500" />)}
              </div>
            </div>
          </div>
          
          <div className="flex justify-end pt-4">
            <button 
              onClick={saveSettings}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-sm"
            >
              <Save size={18} />
              Salvar Configurações
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
