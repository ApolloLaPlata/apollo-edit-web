import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-theme-bg text-theme-text p-4">
      <div className="bg-theme-surface/70 backdrop-blur-2xl border border-theme-accent/30 rounded-3xl p-10 max-w-lg w-full text-center shadow-[0_0_50px_rgba(6,182,212,0.1)]">
        <div className="w-24 h-24 bg-theme-accent/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-theme-accent/20">
          <span className="text-5xl font-black text-theme-accent">404</span>
        </div>
        <h2 className="text-3xl font-black tracking-tight text-white mb-4">Página não encontrada</h2>
        <p className="text-slate-400 font-medium text-sm mb-8 leading-relaxed">
          A matéria ou seção que você está procurando foi movida, excluída ou nunca existiu. 
          Use a busca superior ou retorne à página inicial.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="bg-theme-accent/10 hover:bg-theme-accent text-theme-accent hover:text-white border border-theme-accent/30 hover:border-theme-accent font-bold py-3 px-8 rounded-xl transition-all uppercase tracking-widest text-xs flex items-center justify-center"
            >
              Voltar ao Início
            </Link>
            <Link
              href="/search"
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 hover:border-slate-600 font-bold py-3 px-8 rounded-xl transition-all uppercase tracking-widest text-xs flex items-center justify-center"
            >
              Fazer uma Busca
            </Link>
        </div>
      </div>
    </div>
  );
}
