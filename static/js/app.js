document.addEventListener('DOMContentLoaded', () => {
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view-panel');
    const pageTitle = document.getElementById('page-title');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            navBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');

            // Hide all views
            views.forEach(v => v.classList.add('hidden'));

            // Show targeted view
            const targetId = btn.getAttribute('data-target');
            document.getElementById('view-' + targetId).classList.remove('hidden');

            // Update title
            pageTitle.textContent = btn.textContent;
        });
    });

    // Buscar informações reais do Workspace da API do FastAPI
    fetch('/api/workspace')
        .then(response => response.json())
        .then(data => {
            console.log("Workspace conectado:", data);
        })
        .catch(error => console.error("Erro ao conectar na API:", error));
});
