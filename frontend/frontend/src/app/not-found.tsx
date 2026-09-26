import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center font-sans relative overflow-hidden p-4">
      {/* BACKGROUND EFFECTS */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-red-600/20 blur-[120px] rounded-full mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-cyan-600/10 blur-[100px] rounded-full mix-blend-screen pointer-events-none" />

      {/* GLASSMORPHISM BOX */}
      <div className="z-10 w-full max-w-3xl bg-slate-900/40 backdrop-blur-3xl border border-slate-700/50 rounded-[2rem] shadow-2xl p-8 md:p-16 flex flex-col items-center text-center">
        
        <span className="text-[120px] leading-none md:text-[180px] font-black text-transparent bg-clip-text bg-gradient-to-br from-red-500 to-red-900 drop-shadow-lg mb-4 select-none">
          404
        </span>
        
        <h1 className="text-3xl md:text-5xl font-black text-white mb-6 tracking-tight">
          A Matéria Foi Removida (Ou Moviada)
        </h1>
        
        <p className="text-slate-400 text-lg md:text-xl max-w-xl mb-12 font-medium">
          O link que você acessou expirou. Mas não se preocupe, a inteligência da nossa redação já selecionou os assuntos mais quentes do momento para você.
        </p>

        {/* CASCATA DE LINKS (Retenção) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl mb-10">
          <Link href="/" className="group p-5 bg-slate-800/50 border border-slate-700/50 hover:bg-red-900/20 hover:border-red-500/50 rounded-2xl transition-all duration-300 flex items-center gap-4">
             <span className="w-12 h-12 bg-slate-950 rounded-full flex items-center justify-center text-red-500 font-bold group-hover:scale-110 transition-transform">🔥</span>
             <div className="text-left">
               <h3 className="text-white font-bold text-sm">Notícias em Alta</h3>
               <p className="text-slate-400 text-xs mt-1">Veja o que está bombando hoje.</p>
             </div>
          </Link>

          <Link href="/ofertas" className="group p-5 bg-slate-800/50 border border-slate-700/50 hover:bg-cyan-900/20 hover:border-cyan-500/50 rounded-2xl transition-all duration-300 flex items-center gap-4">
             <span className="w-12 h-12 bg-slate-950 rounded-full flex items-center justify-center text-cyan-500 font-bold group-hover:scale-110 transition-transform">💎</span>
             <div className="text-left">
               <h3 className="text-white font-bold text-sm">Ofertas Exclusivas</h3>
               <p className="text-slate-400 text-xs mt-1">Descontos selecionados por IA.</p>
             </div>
          </Link>
        </div>

        <Link href="/" className="inline-flex items-center justify-center px-8 py-4 bg-white hover:bg-slate-200 text-slate-950 rounded-full font-black uppercase tracking-wider text-sm transition-transform hover:scale-105 active:scale-95 shadow-xl">
          ← Voltar para a Página Inicial
        </Link>
        
      </div>
    </div>
  );
}
