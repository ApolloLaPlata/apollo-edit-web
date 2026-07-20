import React, { useState, useEffect } from 'react';
import { Webhook, Plus, Trash2, Save, Play, CheckCircle2, AlertCircle, Copy } from 'lucide-react';
import { toast } from './Toast';
import { WebhookConfig } from '../lib/webhooks';

export function Integrations() {
  const [configs, setConfigs] = useState<WebhookConfig[]>([]);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('webhook_configs');
    if (stored) {
      try {
        setConfigs(JSON.parse(stored));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const saveConfigs = (newConfigs: WebhookConfig[]) => {
    setConfigs(newConfigs);
    localStorage.setItem('webhook_configs', JSON.stringify(newConfigs));
  };

  const addWebhook = () => {
    const newConfig: WebhookConfig = {
      id: Date.now().toString(),
      name: 'Nova Integração',
      url: 'http://localhost:5000/webhook',
      active: true,
      events: ['script_generated', 'images_exported']
    };
    saveConfigs([...configs, newConfig]);
    setIsEditing(true);
  };

  const updateWebhook = (id: string, field: keyof WebhookConfig, value: any) => {
    const newConfigs = configs.map(c => c.id === id ? { ...c, [field]: value } : c);
    saveConfigs(newConfigs);
  };

  const toggleEvent = (id: string, event: string) => {
    const newConfigs = configs.map(c => {
      if (c.id === id) {
        const events = c.events.includes(event) 
          ? c.events.filter(e => e !== event)
          : [...c.events, event];
        return { ...c, events };
      }
      return c;
    });
    saveConfigs(newConfigs);
  };

  const removeWebhook = (id: string) => {
    saveConfigs(configs.filter(c => c.id !== id));
  };

  const testWebhook = async (webhook: WebhookConfig) => {
    try {
      const response = await fetch(webhook.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event: 'ping',
          timestamp: new Date().toISOString(),
          data: { message: 'Hello from AI Studio!' }
        })
      });
      
      if (response.ok) {
        toast.success(`Conexão com ${webhook.name} bem-sucedida!`);
      } else {
        toast.error(`Erro ao conectar: ${response.statusText}`);
      }
    } catch (error: any) {
      toast.error(`Falha na conexão: ${error.message}`);
    }
  };

  const pythonTemplate = `from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permite receber requisições do navegador

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    event = data.get('event')
    payload = data.get('data')
    
    print(f"Recebido evento: {event}")
    
    if event == 'script_generated':
        print("Roteiro recebido:", payload.get('title'))
        # Salvar em arquivo ou processar
        
    elif event == 'images_exported':
        print(f"Imagens recebidas: {len(payload.get('images', []))}")
        # Salvar imagens localmente
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)`;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-zinc-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-zinc-900 flex items-center gap-2">
              <Webhook className="text-indigo-600" size={28} />
              Integrações & Webhooks
            </h2>
            <p className="text-zinc-600 mt-1">
              Conecte este sistema com seus scripts Python locais ou outras aplicações.
            </p>
          </div>
          <button
            onClick={addWebhook}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            Nova Integração
          </button>
        </div>

        {configs.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-zinc-200 rounded-xl bg-zinc-50">
            <Webhook size={48} className="mx-auto text-zinc-300 mb-3" />
            <h3 className="text-lg font-medium text-zinc-900 mb-1">Nenhuma integração configurada</h3>
            <p className="text-zinc-500 mb-4">Adicione um webhook para enviar dados automaticamente para seus outros sistemas.</p>
            <button
              onClick={addWebhook}
              className="inline-flex items-center gap-2 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <Plus size={16} />
              Adicionar Webhook
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {configs.map(config => (
              <div key={config.id} className="border border-zinc-200 rounded-xl overflow-hidden">
                <div className="bg-zinc-50 p-4 flex items-center justify-between border-b border-zinc-200">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={config.active}
                      onChange={(e) => updateWebhook(config.id, 'active', e.target.checked)}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <input
                      type="text"
                      value={config.name}
                      onChange={(e) => updateWebhook(config.id, 'name', e.target.value)}
                      className="font-medium text-zinc-900 bg-transparent border-none focus:ring-0 p-0"
                      placeholder="Nome da Integração"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => testWebhook(config)}
                      className="flex items-center gap-1 text-xs font-medium text-emerald-600 hover:text-emerald-700 bg-emerald-50 hover:bg-emerald-100 px-2 py-1 rounded transition-colors"
                    >
                      <Play size={14} /> Testar
                    </button>
                    <button
                      onClick={() => removeWebhook(config.id)}
                      className="text-zinc-400 hover:text-red-500 transition-colors p-1"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                
                <div className="p-4 space-y-4 bg-white">
                  <div>
                    <label className="block text-xs font-medium text-zinc-500 mb-1">URL do Webhook (POST)</label>
                    <input
                      type="text"
                      value={config.url}
                      onChange={(e) => updateWebhook(config.id, 'url', e.target.value)}
                      className="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                      placeholder="http://localhost:5000/webhook"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-zinc-500 mb-2">Eventos que disparam este webhook</label>
                    <div className="flex flex-wrap gap-2">
                      <label className="flex items-center gap-2 text-sm bg-zinc-50 px-3 py-1.5 rounded-lg border border-zinc-200 cursor-pointer hover:bg-zinc-100">
                        <input
                          type="checkbox"
                          checked={config.events.includes('script_generated')}
                          onChange={() => toggleEvent(config.id, 'script_generated')}
                          className="text-indigo-600 rounded"
                        />
                        Roteiro Gerado
                      </label>
                      <label className="flex items-center gap-2 text-sm bg-zinc-50 px-3 py-1.5 rounded-lg border border-zinc-200 cursor-pointer hover:bg-zinc-100">
                        <input
                          type="checkbox"
                          checked={config.events.includes('images_exported')}
                          onChange={() => toggleEvent(config.id, 'images_exported')}
                          className="text-indigo-600 rounded"
                        />
                        Imagens Exportadas
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-zinc-900 rounded-xl shadow-sm border border-zinc-800 p-6 text-zinc-300">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            Exemplo de Servidor Python (Flask)
          </h3>
          <button 
            onClick={() => {
              navigator.clipboard.writeText(pythonTemplate);
              toast.success('Código copiado!');
            }}
            className="flex items-center gap-1 text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-2 py-1 rounded transition-colors"
          >
            <Copy size={14} /> Copiar
          </button>
        </div>
        <p className="text-sm mb-4 text-zinc-400">
          Para receber os dados localmente, você precisa de um servidor rodando na sua máquina. 
          Instale as dependências com <code className="bg-zinc-800 px-1 py-0.5 rounded text-indigo-300">pip install flask flask-cors</code> e rode o código abaixo:
        </p>
        <pre className="bg-black p-4 rounded-lg overflow-x-auto text-sm font-mono text-emerald-400 border border-zinc-800">
          {pythonTemplate}
        </pre>
      </div>
    </div>
  );
}
