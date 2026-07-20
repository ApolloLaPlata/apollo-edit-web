import React, { useState, useCallback } from 'react';
import { RefreshCw, Server, CheckCircle2, AlertTriangle, XCircle, Zap, DollarSign, Activity } from 'lucide-react';

interface AccountStatus {
  id: string;
  name: string;
  workspace: string;
  provider: string;
  spent: number | null;
  remaining: number | null;
  budget: number;
  percent_used: number | null;
  status: 'ok' | 'low' | 'exhausted' | 'error';
  error?: string;
}

interface FleetSummary {
  total_accounts: number;
  ok: number;
  low: number;
  exhausted: number;
  total_remaining_usd: number;
  total_spent_usd: number;
  total_budget_usd: number;
  active_for_routing: number;
}

interface FleetData {
  fleet: AccountStatus[];
  summary: FleetSummary;
  lightning: { name: string; workspace: string }[];
}

const statusConfig = {
  ok:        { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', bar: 'bg-emerald-500', label: 'OK' },
  low:       { icon: AlertTriangle, color: 'text-amber-400',  bg: 'bg-amber-500/10 border-amber-500/30',   bar: 'bg-amber-500',   label: 'BAIXO' },
  exhausted: { icon: XCircle,       color: 'text-red-400',    bg: 'bg-red-500/10 border-red-500/30',       bar: 'bg-red-500',     label: 'ESGOTADA' },
  error:     { icon: XCircle,       color: 'text-slate-400',  bg: 'bg-slate-700/50 border-slate-600',      bar: 'bg-slate-600',   label: 'ERRO' },
};

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000');

const FleetStatusPanel: React.FC = () => {
  const [data, setData] = useState<FleetData | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchBalance = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('apollo_token') || '';
      const res = await fetch(`${API_BASE}/api/v1/admin/fleet-balance`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json: FleetData = await res.json();
      setData(json);
      setLastChecked(new Date());
    } catch (e: any) {
      setError(e.message || 'Erro ao consultar fleet');
    } finally {
      setLoading(false);
    }
  }, []);

  const summary = data?.summary;

  return (
    <section className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <Server className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Fleet de Contas Modal</h2>
            <p className="text-slate-400 text-xs">
              Pool de GPU — todas as contas são espelhos, roteadas entre os usuários
            </p>
          </div>
        </div>
        <button
          onClick={fetchBalance}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Verificando...' : 'Verificar Saldo'}
        </button>
      </div>

      {/* Não carregado ainda */}
      {!data && !loading && !error && (
        <div className="text-center py-10 text-slate-500">
          <Server className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Clique em "Verificar Saldo" para checar todas as contas do fleet.</p>
          <p className="text-xs mt-1 opacity-60">A verificação é feita em paralelo e leva ~10-15 segundos.</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-10 text-slate-400">
          <RefreshCw className="w-8 h-8 mx-auto mb-3 animate-spin text-purple-400" />
          <p className="text-sm">Consultando todas as contas em paralelo...</p>
        </div>
      )}

      {/* Erro */}
      {error && !loading && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Dados carregados */}
      {data && !loading && (
        <div className="space-y-5">

          {/* Resumo do Pool */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-slate-900/70 rounded-lg p-3 border border-slate-700">
                <div className="text-xs text-slate-400 mb-1">Ativas p/ Roteamento</div>
                <div className="text-2xl font-bold text-emerald-400">{summary.active_for_routing}</div>
                <div className="text-xs text-slate-500">de {summary.total_accounts} total</div>
              </div>
              <div className="bg-slate-900/70 rounded-lg p-3 border border-slate-700">
                <div className="text-xs text-slate-400 mb-1">Saldo Restante</div>
                <div className="text-2xl font-bold text-white">${summary.total_remaining_usd.toFixed(2)}</div>
                <div className="text-xs text-slate-500">de ${summary.total_budget_usd.toFixed(2)} total</div>
              </div>
              <div className="bg-slate-900/70 rounded-lg p-3 border border-slate-700">
                <div className="text-xs text-slate-400 mb-1">Total Gasto</div>
                <div className="text-2xl font-bold text-amber-400">${summary.total_spent_usd.toFixed(2)}</div>
                <div className="text-xs text-slate-500">este mês</div>
              </div>
              <div className="bg-slate-900/70 rounded-lg p-3 border border-slate-700">
                <div className="text-xs text-slate-400 mb-1">Status</div>
                <div className="flex gap-1.5 flex-wrap mt-1">
                  {summary.ok > 0 && <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-medium">{summary.ok} OK</span>}
                  {summary.low > 0 && <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full font-medium">{summary.low} Baixo</span>}
                  {summary.exhausted > 0 && <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full font-medium">{summary.exhausted} Esgot.</span>}
                </div>
              </div>
            </div>
          )}

          {/* Barra total do pool */}
          {summary && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> Saúde Geral do Pool</span>
                <span>{((summary.total_remaining_usd / summary.total_budget_usd) * 100).toFixed(1)}% disponível</span>
              </div>
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 to-blue-500 transition-all duration-700 rounded-full"
                  style={{ width: `${Math.max(2, (summary.total_remaining_usd / summary.total_budget_usd) * 100)}%` }}
                />
              </div>
            </div>
          )}

          {/* Cards individuais */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
              <Zap className="w-4 h-4 text-purple-400" /> Contas Modal (GPU)
            </h3>
            {data.fleet.map(acc => {
              const cfg = statusConfig[acc.status];
              const Icon = cfg.icon;
              const pct = acc.percent_used ?? 0;
              return (
                <div key={acc.id} className={`rounded-lg border p-3 ${cfg.bg}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-4 h-4 ${cfg.color}`} />
                      <span className="text-sm font-medium text-white">{acc.name}</span>
                      <span className="text-xs text-slate-500 font-mono">{acc.workspace}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      {acc.remaining !== null && (
                        <span className={`text-sm font-bold ${cfg.color}`}>
                          <DollarSign className="w-3 h-3 inline" />{acc.remaining.toFixed(2)} restante
                        </span>
                      )}
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold border ${cfg.bg} ${cfg.color}`}>
                        {cfg.label}
                      </span>
                    </div>
                  </div>
                  {acc.remaining !== null ? (
                    <>
                      <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 rounded-full ${cfg.bar}`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-slate-500 mt-1">
                        <span>Gasto: ${acc.spent?.toFixed(2)}</span>
                        <span>{pct.toFixed(1)}% usado</span>
                      </div>
                    </>
                  ) : (
                    <p className="text-xs text-slate-500 mt-1">{acc.error || 'Sem dados'}</p>
                  )}
                </div>
              );
            })}
          </div>

          {/* Lightning accounts */}
          {data.lightning.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-amber-400" /> Lightning AI (LLM)
              </h3>
              <div className="flex flex-wrap gap-2">
                {data.lightning.map((l, i) => (
                  <span key={i} className="text-xs bg-amber-500/10 border border-amber-500/30 text-amber-400 px-3 py-1 rounded-full font-medium">
                    {l.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Timestamp */}
          {lastChecked && (
            <p className="text-xs text-slate-600 text-right">
              Última verificação: {lastChecked.toLocaleTimeString('pt-BR')}
            </p>
          )}
        </div>
      )}
    </section>
  );
};

export default FleetStatusPanel;
