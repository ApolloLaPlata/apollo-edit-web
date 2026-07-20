export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 pb-20 gap-16 sm:p-20 relative overflow-hidden">
      
      {/* Background Decorators */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-500/10 rounded-full blur-[100px] -z-10 pointer-events-none"></div>

      <main className="flex flex-col gap-8 row-start-2 items-center text-center z-10">
        <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600 drop-shadow-sm">
          Apollo Edit Web
        </h1>
        <p className="text-lg sm:text-xl text-gray-500 max-w-2xl font-light">
          O motor de automação inteligente e laboratório de validação contínua para o Auto Blog CMS.
        </p>

        <div className="flex gap-4 items-center flex-col sm:flex-row mt-8">
          <a
            className="rounded-full border border-solid border-transparent transition-all duration-300 flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] text-sm sm:text-base h-12 px-8 font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            href="#"
          >
            Painel de Controle
          </a>
          <a
            className="rounded-full border-2 border-solid border-gray-200 dark:border-gray-800 transition-all duration-300 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-900 hover:border-gray-300 dark:hover:border-gray-700 text-sm sm:text-base h-12 px-8 font-medium"
            href="#"
          >
            Ver Artigos (MVP)
          </a>
        </div>
      </main>

      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center text-sm text-gray-400 absolute bottom-8">
        <p>© 2026 Apollo Edit Web - Monorepo Vercel Deployment</p>
      </footer>
    </div>
  );
}
