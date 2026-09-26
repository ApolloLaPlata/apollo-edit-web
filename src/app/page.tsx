export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-slate-950 text-white">
      <main className="flex flex-col gap-8 row-start-2 items-center text-center">
        <h1 className="text-5xl font-bold text-blue-500 tracking-tight">Apollo Edit Web</h1>
        <p className="text-xl text-slate-400 max-w-2xl">
          O Motor de Edição de Vídeo Automatizado da Colmeia V5.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <div className="px-6 py-3 rounded-full bg-blue-600/20 text-blue-400 border border-blue-600/30 font-medium">
            Next.js App Router Integrado
          </div>
          <div className="px-6 py-3 rounded-full bg-green-600/20 text-green-400 border border-green-600/30 font-medium">
            FFmpeg Orquestration Ready
          </div>
        </div>
      </main>
    </div>
  );
}