import React from 'react';
import { LineChart, TrendingUp, TrendingDown, Users, MessageSquare, Eye, Twitter, Youtube, Instagram, Facebook, Video, Activity, RefreshCw } from 'lucide-react';

export function Dashboard() {
  // Mock data for the dashboard preview
  const stats = [
    { name: 'Total de Seguidores', value: '1.2M', change: '+12.5%', isPositive: true, icon: Users },
    { name: 'Visualizações (7d)', value: '4.8M', change: '+5.2%', isPositive: true, icon: Eye },
    { name: 'Engajamento Médio', value: '8.4%', change: '-1.1%', isPositive: false, icon: Activity },
    { name: 'Comentários (24h)', value: '12.4K', change: '+24.8%', isPositive: true, icon: MessageSquare },
  ];

  const networks = [
    { name: 'YouTube', icon: Youtube, color: 'text-red-500', bg: 'bg-red-50', followers: '450K', growth: '+2.1K', status: 'active' },
    { name: 'Instagram', icon: Instagram, color: 'text-pink-600', bg: 'bg-pink-50', followers: '320K', growth: '+1.5K', status: 'active' },
    { name: 'TikTok', icon: Video, color: 'text-black', bg: 'bg-zinc-100', followers: '280K', growth: '+4.2K', status: 'active' },
    { name: 'Kwai', icon: Video, color: 'text-orange-500', bg: 'bg-orange-50', followers: '110K', growth: '+800', status: 'active' },
    { name: 'Facebook', icon: Facebook, color: 'text-blue-600', bg: 'bg-blue-50', followers: '85K', growth: '-120', status: 'warning' },
    { name: 'X (Twitter)', icon: Twitter, color: 'text-sky-500', bg: 'bg-sky-50', followers: '45K', growth: '+300', status: 'active' },
  ];

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 flex items-center gap-2">
            <LineChart className="text-indigo-600" />
            Dashboard de Audiência
          </h2>
          <p className="text-zinc-500 mt-1">Monitoramento em tempo real de todas as suas redes sociais.</p>
        </div>
        
        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-zinc-200 text-zinc-700 rounded-lg hover:bg-zinc-50 transition-colors shadow-sm text-sm font-medium">
          <RefreshCw size={16} />
          Sincronizar Dados
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg bg-indigo-50 text-indigo-600`}>
                <stat.icon size={20} />
              </div>
              <div className={`flex items-center gap-1 text-sm font-medium ${stat.isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                {stat.isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {stat.change}
              </div>
            </div>
            <h3 className="text-3xl font-bold text-zinc-900 mb-1">{stat.value}</h3>
            <p className="text-sm text-zinc-500 font-medium">{stat.name}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Networks Breakdown */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-zinc-100">
            <h3 className="text-lg font-semibold text-zinc-900">Desempenho por Rede</h3>
          </div>
          <div className="divide-y divide-zinc-100">
            {networks.map((network, i) => (
              <div key={i} className="p-4 sm:p-6 flex items-center justify-between hover:bg-zinc-50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl ${network.bg} ${network.color}`}>
                    <network.icon size={24} />
                  </div>
                  <div>
                    <h4 className="font-semibold text-zinc-900">{network.name}</h4>
                    <p className="text-sm text-zinc-500">Última atualização há 5 min</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="font-bold text-zinc-900 text-lg">{network.followers}</div>
                  <div className={`text-sm font-medium flex items-center justify-end gap-1 ${network.status === 'warning' ? 'text-red-600' : 'text-emerald-600'}`}>
                    {network.status === 'warning' ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                    {network.growth} inscritos hoje
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Comments / Alerts */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-zinc-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-zinc-900 mb-4">Alertas de Audiência</h3>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-red-50 border border-red-100">
                <div className="flex items-start gap-3">
                  <TrendingDown className="text-red-600 mt-0.5" size={18} />
                  <div>
                    <h4 className="text-sm font-bold text-red-900">Queda no Facebook</h4>
                    <p className="text-xs text-red-700 mt-1">Seu último vídeo teve 40% menos alcance que a média. Considere mudar o formato.</p>
                  </div>
                </div>
              </div>
              
              <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-100">
                <div className="flex items-start gap-3">
                  <TrendingUp className="text-emerald-600 mt-0.5" size={18} />
                  <div>
                    <h4 className="text-sm font-bold text-emerald-900">Pico no TikTok</h4>
                    <p className="text-xs text-emerald-700 mt-1">O vídeo "Notícias de Hoje" está viralizando. +4.2k seguidores nas últimas 2 horas.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-indigo-600 rounded-xl shadow-sm p-6 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Activity size={100} />
            </div>
            <h3 className="text-lg font-semibold mb-2 relative z-10">Próximos Passos</h3>
            <p className="text-indigo-100 text-sm mb-4 relative z-10">
              Conecte suas chaves de API na aba de Configurações para substituir estes dados de demonstração pelos seus dados reais.
            </p>
            <button className="bg-white text-indigo-600 px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-indigo-50 transition-colors relative z-10">
              Ir para Configurações
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
