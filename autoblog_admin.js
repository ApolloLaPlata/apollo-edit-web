document.addEventListener('DOMContentLoaded', async () => {
    console.log("Inicializando Central Auto Blog...");
    
    // Aguardar a inicialização do auth.js (window.supabase)
    let checks = 0;
    const checkSupabase = setInterval(async () => {
        if (window.supabase) {
            clearInterval(checkSupabase);
            await checkSession();
            await loadBlogs();
        }
        if (checks++ > 20) {
            clearInterval(checkSupabase);
            document.getElementById('userEmail').innerText = "Erro ao carregar cliente DB.";
        }
    }, 100);

    // Event Listener for New Blog Form
    document.getElementById('newBlogForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const domain = document.getElementById('bDomain').value;
        const name = document.getElementById('bName').value;
        const niche = document.getElementById('bNiche').value;
        
        const btn = document.getElementById('btnSaveBlog');
        btn.innerHTML = '<span class="loading loading-spinner"></span> Salvando...';
        btn.disabled = true;

        const blogId = crypto.randomUUID();

        try {
            const { error } = await window.supabase.from('Blog').insert([
                { id: blogId, domain, name, niche }
            ]);

            if (error) throw error;

            alert('Blog criado com sucesso! Agora o robô escritor já pode acessá-lo.');
            document.getElementById('newBlogForm').reset();
            document.getElementById('modalNewBlog').close();
            await loadBlogs();
        } catch (err) {
            console.error(err);
            alert('Erro ao salvar blog. Certifique-se que você rodou o script SQL no Supabase.');
        } finally {
            btn.innerHTML = 'Salvar na Rede';
            btn.disabled = false;
        }
    });
});

async function checkSession() {
    const { data: { session } } = await window.supabase.auth.getSession();
    if (session) {
        document.getElementById('userEmail').innerText = session.user.email;
    } else {
        document.getElementById('userEmail').innerText = "Usuário Desconectado - Leitura Local";
    }
}

async function loadBlogs() {
    const grid = document.getElementById('blogGrid');
    
    try {
        const { data: blogs, error } = await window.supabase
            .from('Blog')
            .select('*')
            .order('createdAt', { ascending: false });
            
        if (error) throw error;

        grid.innerHTML = '';
        
        if (!blogs || blogs.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center py-12 glass-panel rounded-xl">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
                    <h3 class="text-xl font-bold text-gray-300">Nenhum Auto-Blog Encontrado</h3>
                    <p class="text-gray-500 mt-2">Comece criando o primeiro domínio para a IA gerenciar.</p>
                </div>
            `;
            return;
        }

        blogs.forEach(blog => {
            const card = document.createElement('div');
            card.className = 'glass-panel p-6 rounded-xl border-t-4 hover:shadow-lg transition flex flex-col justify-between';
            card.style.borderTopColor = blog.primaryColor || '#3b82f6';
            
            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-start mb-2">
                        <h2 class="text-2xl font-bold text-white">${blog.name}</h2>
                        <span class="badge badge-primary badge-outline text-xs uppercase">${blog.niche}</span>
                    </div>
                    <a href="https://${blog.domain}" target="_blank" class="text-sm text-blue-400 hover:underline mb-4 block flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                        ${blog.domain}
                    </a>
                </div>
                <div class="mt-6 flex gap-2">
                    <button class="btn btn-sm btn-outline flex-1" onclick="alert('Funcionalidade de Gestão de Robôs em breve!')">Robô IA</button>
                    <button class="btn btn-sm btn-outline flex-1" onclick="alert('Ver fila de Posts em breve!')">Posts</button>
                </div>
            `;
            grid.appendChild(card);
        });

    } catch (err) {
        console.error("Erro ao carregar blogs:", err);
        grid.innerHTML = `
            <div class="col-span-full glass-panel p-6 rounded-xl border-red-500 border-l-4">
                <h3 class="text-red-400 font-bold">Erro de Conexão</h3>
                <p class="text-sm text-gray-400">Você já executou o script SQL no Supabase para criar a tabela 'Blog'?</p>
            </div>
        `;
    }
}
