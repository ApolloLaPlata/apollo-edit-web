'use client';
import React, { useEffect, useState } from 'react';

export default function ReportsClient() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any | null>(null);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/reports');
      const json = await res.json();
      if (json.success) {
        setData(json);
      } else {
        showToast('error', json.error || 'Falha ao carregar dados de auditoria.');
      }
    } catch (e) {
      showToast('error', 'Erro de conexão com o servidor de telemetria.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // Helper para exportar CSV
  const exportCSV = (items: any[], filename: string) => {
    if (!items || items.length === 0) {
      showToast('error', 'Nenhum dado disponível para exportação.');
      return;
    }
    const headers = Object.keys(items[0]);
    const csvRows = [
      headers.join(','),
      ...items.map((row) =>
        headers
          .map((fieldName) => {
            const val = row[fieldName] === null || row[fieldName] === undefined ? '' : row[fieldName];
            return `"${String(val).replace(/"/g, '""')}"`;
          })
          .join(',')
      ),
    ];
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    showToast('success', `Arquivo CSV ${filename} exportado com sucesso!`);
  };

  // Helper para exportar JSON
  const exportJSON = (items: any, filename: string) => {
    if (!items) {
      showToast('error', 'Nenhum dado disponível para exportação.');
      return;
    }
    const blob = new Blob([JSON.stringify(items, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    showToast('success', `Arquivo JSON ${filename} exportado com sucesso!`);
  };

  // Helper para gerar o Briefing Executivo em Markdown
  const getBriefingMarkdown = () => {
    if (!data?.briefing) return '';
    const b = data.briefing;
    return `# 📊 BRIEFING EXECUTIVO DE AUDITORIA — AUTO-BLOG CMS
**Data da Auditoria:** ${new Date().toLocaleDateString('pt-BR')} às ${new Date().toLocaleTimeString('pt-BR')}
**Status do Sistema:** Operacional • Colmeia Neural v2.0

---

## 📈 1. RESUMO GERAL DA FROTA
- **Portais Ativos na Frota:** ${b.totalBlogs} veículos
- **Categorias Mapeadas:** ${b.totalCategories} nichos editoriais
- **Total de Reportagens no Banco:** ${b.totalPosts} artigos
- **Matérias Publicadas:** ${b.publishedPosts} reportagens no ar
- **Taxa de Publicação Ativa:** ${b.totalPosts > 0 ? ((b.publishedPosts / b.totalPosts) * 100).toFixed(1) : 0}%

---

## 🌐 2. TELEMETRIA DE CROSS-CHANNEL & SINDICÂNCIA
- **Matérias Sindicadas na Rede Apollo:** ${b.totalSyndicated} artigos
- **Impacto em Backlinks Internos:** ${b.totalSyndicated * 2} backlinks canônicos ativos
- **Status do Motor de Sindicato:** Online (Canonical SEO Preserved)

---

## 💰 3. AUDITORIA DE MONETIZAÇÃO & AFILIADOS
- **Inventário de Links Patrocinados:** ${b.totalAffiliateLinks} campanhas ativas
- **Total de Cliques Computados:** ${b.totalAffiliateClicks} cliques reais registrados
- **Desempenho Médio por Campanha:** ${b.totalAffiliateLinks > 0 ? (b.totalAffiliateClicks / b.totalAffiliateLinks).toFixed(1) : 0} cliques/link

---

*Relatório gerado automaticamente pela Central de Inteligência e Auditoria da Colmeia.*
`;
  };

  const copyBriefing = () => {
    const text = getBriefingMarkdown();
    navigator.clipboard.writeText(text);
    showToast('success', 'Briefing Executivo copiado para a área de transferência!');
  };

  const downloadBriefing = () => {
    const text = getBriefingMarkdown();
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `briefing_executivo_apollo_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    showToast('success', 'Briefing Markdown baixado com sucesso!');
  };

  const exportPDF = () => {
    if (!data?.briefing) {
      showToast('error', 'Sem dados de auditoria para compilar PDF.');
      return;
    }
    const b = data.briefing;
    const printWindow = window.open('', '_blank', 'width=900,height=1100');
    if (!printWindow) {
      showToast('error', 'O bloqueador de popups impediu a geração do PDF. Permita popups para o portal.');
      return;
    }
    const html = `
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <title>Dossiê Executivo de Auditoria - Auto-Blog CMS</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@700&display=swap');
          @page { size: A4; margin: 25mm 20mm; }
          body { font-family: 'Inter', sans-serif; color: #0f172a; background: #ffffff; margin: 0; padding: 0; line-height: 1.6; }
          .header { border-bottom: 3px solid #0f172a; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
          .title { font-size: 26px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; color: #0f172a; margin: 0; }
          .subtitle { font-size: 13px; color: #64748b; margin-top: 4px; font-weight: 600; }
          .badge { background: #0f172a; color: #ffffff; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
          .section-title { font-size: 16px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; }
          .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
          .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; }
          .card-label { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; }
          .card-val { font-size: 24px; font-weight: 800; color: #0f172a; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }
          .table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }
          .table th { background: #0f172a; color: #ffffff; text-align: left; padding: 10px; font-weight: 600; text-transform: uppercase; font-size: 11px; }
          .table td { padding: 10px; border-bottom: 1px solid #e2e8f0; color: #334155; }
          .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <h1 class="title">Dossiê de Auditoria & Telemetria</h1>
            <div class="subtitle">Sistema Operacional: Auto-Blog CMS • Colmeia Neural v2.0</div>
          </div>
          <div class="badge">CONFIDENCIAL • COMPLIANCE</div>
        </div>

        <div class="section-title">1. Desempenho e Produtividade Editorial</div>
        <div class="grid">
          <div class="card">
            <div class="card-label">Portais Ativos na Frota</div>
            <div class="card-val">${b.totalBlogs || 0} Veículos</div>
          </div>
          <div class="card">
            <div class="card-label">Nichos & Categorias</div>
            <div class="card-val">${b.totalCategories || 0} Categorias</div>
          </div>
          <div class="card">
            <div class="card-label">Artigos Redigidos</div>
            <div class="card-val">${b.totalPosts || 0} Reportagens</div>
          </div>
          <div class="card">
            <div class="card-label">Matérias Publicadas (Online)</div>
            <div class="card-val">${b.publishedPosts || 0} Publicadas</div>
          </div>
        </div>

        <div class="section-title">2. Monetização de Afiliados & Links Patrocinados</div>
        <div class="grid">
          <div class="card">
            <div class="card-label">Campanhas / Palavras-Chave Ativas</div>
            <div class="card-val">${b.totalAffiliateLinks || 0} Campanhas</div>
          </div>
          <div class="card">
            <div class="card-label">Cliques de Monetização Reais</div>
            <div class="card-val">${b.totalAffiliateClicks || 0} Cliques</div>
          </div>
        </div>

        <div class="section-title">3. Cross-Channel & Sindicato Neural</div>
        <div class="grid">
          <div class="card">
            <div class="card-label">Matérias Sindicadas na Frota</div>
            <div class="card-val">${b.totalSyndicated || 0} Artigos</div>
          </div>
          <div class="card">
            <div class="card-label">Backlinks SEO Gerados</div>
            <div class="card-val">${(b.totalSyndicated || 0) * 2} Backlinks</div>
          </div>
        </div>

        <div class="section-title">4. Últimas Matérias Registradas no Sistema</div>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Título da Reportagem</th>
              <th>Status</th>
              <th>Data de Emissão</th>
            </tr>
          </thead>
          <tbody>
            ${(data.posts || []).slice(0, 8).map((p: any) => {
              const bg = p.isPublished ? '#dcfce7' : '#f1f5f9';
              const color = p.isPublished ? '#166534' : '#475569';
              const statusText = p.isPublished ? 'PUBLICADO' : 'RASCUNHO';
              return '<tr><td style="font-family: monospace; font-weight: bold;">#' + p.id + '</td><td style="font-weight: 600;">' + p.title + '</td><td><span style="background: ' + bg + '; color: ' + color + '; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 10px;">' + statusText + '</span></td><td>' + p.createdAt + '</td></tr>';
            }).join('')}
          </tbody>
        </table>

        <div class="footer">
          <div>Gerado automaticamente pelo Motor Executivo Apollo</div>
          <div>Data de Emissão: ${new Date().toLocaleDateString('pt-BR')} ${new Date().toLocaleTimeString('pt-BR')}</div>
        </div>
        <script>
          window.onload = () => {
            setTimeout(() => {
              window.print();
            }, 500);
          };
        </script>
      </body>
      </html>
    `;
    printWindow.document.write(html);
    printWindow.document.close();
    showToast('success', 'Dossiê Executivo PDF gerado e aberto para impressão/salvamento!');
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium text-sm tracking-wide animate-pulse">
          Gerando relatórios de auditoria e telemetria da frota...
        </p>
      </div>
    );
  }

  const briefing = data?.briefing || {};
  const posts = data?.posts || [];
  const affiliateLinks = data?.affiliateLinks || [];
  const syndicatedPosts = data?.syndicatedPosts || [];

  return (
    <div className="space-y-10 relative">
      {/* TOAST EXECUTIVO */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/90 border-red-500/50 text-red-300'
          }`}
        >
          <span className="text-lg">{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span className="text-xs font-semibold">{toast.message}</span>
          <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      {/* HEADER CORPORATIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-amber-500/10 via-orange-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              AUDITORIA & TELEMETRIA ENTERPRISE
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Central de Auditoria & Relatórios
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Exporte dados brutos de redação, cliques monetizados e sindicância em formatos padrão corporativo (.csv, .json e .md) para análise externa e prestação de contas.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Frota Ativa</span>
              <span className="text-2xl font-extrabold text-white font-mono">{briefing.totalBlogs || 0}</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Publicados</span>
              <span className="text-2xl font-extrabold text-amber-400 font-mono">{briefing.publishedPosts || 0}</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Cliques Ads</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">{briefing.totalAffiliateClicks || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* PAINEL DE BRIEFING EXECUTIVO INTERATIVO */}
      <div className="bg-slate-900/60 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800/80 shadow-2xl space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800/80 pb-6">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>📋</span> Briefing Executivo em Tempo Real
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Resumo consolidado do status do império editorial, pronto para apresentação executiva ou envio por e-mail.
            </p>
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={copyBriefing}
              className="flex-1 md:flex-initial bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white px-4 py-2.5 rounded-xl text-xs font-bold transition-all border border-slate-700/80 flex items-center justify-center gap-2"
            >
              <span>📋</span> Copiar (.md)
            </button>
            <button
              onClick={downloadBriefing}
              className="flex-1 md:flex-initial bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white px-4 py-2.5 rounded-xl text-xs font-bold transition-all border border-amber-500/30 hover:border-amber-500 shadow-sm flex items-center justify-center gap-2"
            >
              <span>⬇️</span> Baixar (.md)
            </button>
            <button
              onClick={exportPDF}
              className="flex-1 md:flex-initial bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white px-4 py-2.5 rounded-xl text-xs font-bold transition-all border border-emerald-500/30 hover:border-emerald-500 shadow-sm flex items-center justify-center gap-2"
            >
              <span>📄</span> Exportar PDF Executivo
            </button>
          </div>
        </div>

        <div className="bg-slate-950/80 p-6 rounded-2xl border border-slate-800/80 font-mono text-xs text-slate-300 space-y-4 overflow-x-auto max-h-96 custom-scrollbar">
          <pre className="whitespace-pre-wrap font-sans leading-relaxed text-slate-300">{getBriefingMarkdown()}</pre>
        </div>
      </div>

      {/* CARDS DE EXPORTAÇÃO DE DADOS BRUTOS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* CARD 1: RELATÓRIO EDITORIAL */}
        <div className="bg-slate-900/60 backdrop-blur-2xl p-6 rounded-3xl border border-slate-800/80 shadow-xl flex flex-col justify-between hover:border-blue-500/40 transition-all">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center text-2xl font-bold">
              📝
            </div>
            <h3 className="text-lg font-bold text-white">Relatório Editorial Completo</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Contém todos os {posts.length} artigos cadastrados no banco SQLite, incluindo portal de origem, autor IA, status de publicação e data de criação.
            </p>
          </div>
          <div className="pt-6 mt-6 border-t border-slate-800/80 flex gap-3">
            <button
              onClick={() => exportCSV(posts, 'relatorio_editorial_apollo')}
              className="flex-1 bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-blue-500/30 text-center"
            >
              ⬇️ Baixar .CSV
            </button>
            <button
              onClick={() => exportJSON(posts, 'relatorio_editorial_apollo')}
              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-slate-700 text-center"
            >
              ⬇️ Baixar .JSON
            </button>
          </div>
        </div>

        {/* CARD 2: AUDITORIA DE MONETIZAÇÃO */}
        <div className="bg-slate-900/60 backdrop-blur-2xl p-6 rounded-3xl border border-slate-800/80 shadow-xl flex flex-col justify-between hover:border-emerald-500/40 transition-all">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-2xl font-bold">
              💰
            </div>
            <h3 className="text-lg font-bold text-white">Auditoria de Receita & Afiliados</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Exportação de telemetria de todas as {affiliateLinks.length} campanhas ativas e totalização de cliques monetizados na frota.
            </p>
          </div>
          <div className="pt-6 mt-6 border-t border-slate-800/80 flex gap-3">
            <button
              onClick={() => exportCSV(affiliateLinks, 'auditoria_monetizacao_apollo')}
              className="flex-1 bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-emerald-500/30 text-center"
            >
              ⬇️ Baixar .CSV
            </button>
            <button
              onClick={() => exportJSON(affiliateLinks, 'auditoria_monetizacao_apollo')}
              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-slate-700 text-center"
            >
              ⬇️ Baixar .JSON
            </button>
          </div>
        </div>

        {/* CARD 3: TELEMETRIA DE SINDICÂNCIA */}
        <div className="bg-slate-900/60 backdrop-blur-2xl p-6 rounded-3xl border border-slate-800/80 shadow-xl flex flex-col justify-between hover:border-cyan-500/40 transition-all">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center text-2xl font-bold">
              🌐
            </div>
            <h3 className="text-lg font-bold text-white">Telemetria de Cross-Channel</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Auditoria de todos os {syndicatedPosts.length} artigos republicados na rede Apollo, com mapeamento de backlinks internos e canônicos.
            </p>
          </div>
          <div className="pt-6 mt-6 border-t border-slate-800/80 flex gap-3">
            <button
              onClick={() => exportCSV(syndicatedPosts, 'telemetria_sindicancia_apollo')}
              className="flex-1 bg-cyan-600/20 hover:bg-cyan-600 text-cyan-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-cyan-500/30 text-center"
            >
              ⬇️ Baixar .CSV
            </button>
            <button
              onClick={() => exportJSON(syndicatedPosts, 'telemetria_sindicancia_apollo')}
              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all border border-slate-700 text-center"
            >
              ⬇️ Baixar .JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
