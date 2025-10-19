// SOMA/soma_app/static/js/theme.js

console.log("Theme script loaded.");

document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('theme-toggle');
    const body = document.body;
    const sunIcon = toggleButton.querySelector('.fa-sun');
    const moonIcon = toggleButton.querySelector('.fa-moon');

    // 1. Verifica se há uma preferência de tema salva no armazenamento local
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        // Mostra a lua (porque o tema já é escuro)
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'inline';
    } else {
        // Mostra o sol (porque o tema é claro)
        sunIcon.style.display = 'inline';
        moonIcon.style.display = 'none';
    }

    // 2. Adiciona o listener para alternar o tema ao clicar
    toggleButton.addEventListener('click', () => {
        
        // Alterna a classe 'dark-mode' no corpo do documento
        body.classList.toggle('dark-mode');

        // Salva a nova preferência no armazenamento local
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline';
        } else {
            localStorage.setItem('theme', 'light');
            sunIcon.style.display = 'inline';
            moonIcon.style.display = 'none';
        }
    });

    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            // Alterna a classe 'sidebar-active' no corpo do documento
            body.classList.toggle('sidebar-active');
        });
        
        // Opcional: Fechar o sidebar ao clicar em um item de menu (em telas pequenas)
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        sidebarItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    body.classList.remove('sidebar-active');
                }
            });
        });
    }
});