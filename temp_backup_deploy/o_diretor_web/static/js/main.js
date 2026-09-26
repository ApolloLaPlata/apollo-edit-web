document.addEventListener('DOMContentLoaded', () => {
    console.log('O Diretor Web inicializado com sucesso!');

    // Efeito simples de clique nos itens da navegação
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Se for link interno (href="#")
            if (link.getAttribute('href') === '#') {
                e.preventDefault();
                navLinks.forEach(l => l.parentElement.classList.remove('active'));
                link.parentElement.classList.add('active');
                
                const moduleName = link.querySelector('span').innerText;
                console.log(`Navegando para o módulo: ${moduleName}`);
            }
        });
    });
});
