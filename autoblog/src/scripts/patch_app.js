const fs = require('fs');
const path = require('path');

const filePath = path.resolve(__dirname, 'src', 'app', 'admin', 'appearance', 'AppearanceClient.tsx');
let content = fs.readFileSync(filePath, 'utf8');

// 1. Atualizar Interface Blog
content = content.replace(
  'layoutStyle?: string;',
  'layoutStyle?: string;\n  bgPrimary?: string;\n  bgSurface?: string;\n  fontHeading?: string;\n  fontBody?: string;\n  bannerUrl?: string;'
);

// 2. Atualizar estado 'form'
content = content.replace(
  "primaryColor: currentBlog?.primaryColor || '#06b6d4',",
  "primaryColor: currentBlog?.primaryColor || '#06b6d4',\n    bgPrimary: currentBlog?.bgPrimary || '#020617',\n    bgSurface: currentBlog?.bgSurface || '#1e293b',\n    fontHeading: currentBlog?.fontHeading || 'Inter',\n    fontBody: currentBlog?.fontBody || 'Inter',\n    bannerUrl: currentBlog?.bannerUrl || '',"
);

// 3. Atualizar o setForm no handleSelectBlog
content = content.replace(
  "primaryColor: blog.primaryColor || '#06b6d4',",
  "primaryColor: blog.primaryColor || '#06b6d4',\n      bgPrimary: blog.bgPrimary || '#020617',\n      bgSurface: blog.bgSurface || '#1e293b',\n      fontHeading: blog.fontHeading || 'Inter',\n      fontBody: blog.fontBody || 'Inter',\n      bannerUrl: blog.bannerUrl || '',"
);

// 4. Injetar Inputs no HTML (Cores)
const colorsHtmlOriginal = `                {/* PALETA DE CORES CUSTOM */}
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                    <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Cor Primária</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800">
                    <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Cor Secundária</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-full bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                </div>`;

const newColorsHtml = `                {/* MOTOR DE CORES AVANÇADO (V3) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="bg-[#150a21] p-3.5 rounded-2xl border border-purple-900/50">
                    <label className="block text-[11px] font-bold text-purple-300 uppercase tracking-wider mb-2">Fundo Mestre (bgPrimary)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.bgPrimary} onChange={(e) => setForm({ ...form, bgPrimary: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.bgPrimary} onChange={(e) => setForm({ ...form, bgPrimary: e.target.value })} className="w-full bg-black border border-purple-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#150a21] p-3.5 rounded-2xl border border-purple-900/50">
                    <label className="block text-[11px] font-bold text-purple-300 uppercase tracking-wider mb-2">Fundo Conteúdo (bgSurface)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.bgSurface} onChange={(e) => setForm({ ...form, bgSurface: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.bgSurface} onChange={(e) => setForm({ ...form, bgSurface: e.target.value })} className="w-full bg-black border border-purple-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#1a1405] p-3.5 rounded-2xl border border-yellow-900/50">
                    <label className="block text-[11px] font-bold text-yellow-500 uppercase tracking-wider mb-2">Cor Primária (Accent)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-full bg-black border border-yellow-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#1a1405] p-3.5 rounded-2xl border border-yellow-900/50">
                    <label className="block text-[11px] font-bold text-yellow-500 uppercase tracking-wider mb-2">Cor Secundária</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-full bg-black border border-yellow-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                </div>`;

content = content.replace(colorsHtmlOriginal, newColorsHtml);

// 5. Injetar Inputs de Tipografia customizada em formato TEXTO
const typographyHtmlOriginal = `                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Família Tipográfica Principal</label>
                <div className="grid grid-cols-1 gap-2.5 max-h-[380px] overflow-y-auto pr-1">
                  {FONT_PRESETS.map((fp) => (
                    <button
                      key={fp.id}
                      type="button"
                      onClick={() => setForm({ ...form, fontFamily: fp.id })}
                      className={\`w-full p-3.5 rounded-xl border text-left transition-all flex items-center justify-between \${form.fontFamily === fp.id ? 'bg-slate-950 text-white shadow-md' : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'}\`}
                      style={form.fontFamily === fp.id ? { borderColor: form.primaryColor, boxShadow: \`0 0 15px \${form.primaryColor}15\` } : {}}
                    >
                      <div>
                        <div className="text-sm font-bold text-white mb-0.5" style={{ fontFamily: fp.family }}>{fp.label}</div>
                        <div className="text-[10px] text-slate-500 font-mono">{fp.desc}</div>
                      </div>
                      <div className="text-lg font-bold opacity-60" style={{ fontFamily: fp.family }}>
                        Aa Bb
                      </div>
                    </button>
                  ))}
                </div>`;

const newTypographyHtml = `                <div className="space-y-4 bg-gradient-to-br from-black to-[#0a0514] p-5 rounded-2xl border border-purple-500/20 shadow-xl">
                  <div className="bg-purple-900/20 text-purple-300 p-3 rounded-xl border border-purple-800/30 text-xs">
                    💡 <strong>Motor V3:</strong> Insira os nomes exatos do <em>Google Fonts</em>. O sistema irá importar dinamicamente (Ex: "Space Grotesk", "DM Serif Display").
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2">Fonte dos Títulos (Heading)</label>
                    <input type="text" value={form.fontHeading} onChange={(e) => setForm({ ...form, fontHeading: e.target.value })} className="w-full bg-black border border-purple-900/50 rounded-xl p-3 text-sm font-bold text-white focus:outline-none focus:border-purple-500 transition-all" placeholder="Ex: Playfair Display" />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2">Fonte do Corpo (Body)</label>
                    <input type="text" value={form.fontBody} onChange={(e) => setForm({ ...form, fontBody: e.target.value })} className="w-full bg-black border border-purple-900/50 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-purple-500 transition-all" placeholder="Ex: Inter" />
                  </div>
                </div>`;

content = content.replace(typographyHtmlOriginal, newTypographyHtml);

// 6. Adicionar o input de BANNER na seção BRANDING
const logoInputHtml = `                  <div>
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Logomarca (URL SVG/PNG)</label>
                    <input type="text" value={form.logoUrl} onChange={(e) => setForm({ ...form, logoUrl: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 focus:outline-none transition-all" placeholder="https://..." />
                  </div>`;

const logoAndBannerHtml = `                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-yellow-500 uppercase tracking-wider mb-1.5">👑 Logomarca Exclusiva (URL)</label>
                      <input type="text" value={form.logoUrl} onChange={(e) => setForm({ ...form, logoUrl: e.target.value })} className="w-full bg-black border border-yellow-900/50 rounded-xl p-3 text-xs text-slate-300 focus:outline-none focus:border-yellow-500 transition-all" placeholder="https://..." />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-purple-400 uppercase tracking-wider mb-1.5">🌌 Banner Principal (URL)</label>
                      <input type="text" value={form.bannerUrl} onChange={(e) => setForm({ ...form, bannerUrl: e.target.value })} className="w-full bg-black border border-purple-900/50 rounded-xl p-3 text-xs text-slate-300 focus:outline-none focus:border-purple-500 transition-all" placeholder="Link de imagem para fundo do cabeçalho" />
                    </div>
                  </div>`;

content = content.replace(logoInputHtml, logoAndBannerHtml);

// 7. Pintar o cabeçalho
const oldHeader = 'className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6"';
const newHeader = 'className="bg-[#050012]/90 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-purple-900/50 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6"';
content = content.replace(oldHeader, newHeader);

const oldTitle = 'className="text-3xl md:text-4xl font-extrabold text-white tracking-tight"';
const newTitle = 'className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-yellow-500 to-purple-400 tracking-tight"';
content = content.replace(oldTitle, newTitle);

fs.writeFileSync(filePath, content, 'utf8');
console.log('PATCH UI concluído!');
