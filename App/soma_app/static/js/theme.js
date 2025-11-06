// SOMA/soma_app/static/js/theme.js

// 🚨 NOVA FUNÇÃO PARA TROCAR OS SVGs
function updateLogoSource(isDarkMode) {
    // Seleciona todas as imagens que têm os data attributes de logos
    const logos = document.querySelectorAll('[data-logo-dark], [data-logo-light]');
    
    logos.forEach(logo => {
        const darkSrc = logo.getAttribute('data-logo-dark');
        const lightSrc = logo.getAttribute('data-logo-light');
        
        // Verifica se o elemento atual é a logo do cabeçalho
        if (logo.classList.contains('header-logo')) {
            // A logo do cabeçalho usa a cor de fundo/header
            logo.src = isDarkMode ? darkSrc : lightSrc;
            
        // Verifica se o elemento atual é a logo "Sobre o SOMA"
        } else if (logo.classList.contains('about-soma-logo')) {
            // A logo "Sobre o SOMA" usa o fundo do cartão (que inverte)
            // No modo escuro (fundo escuro do cartão), usa a logo clara (darkSrc)
            // No modo claro (fundo claro do cartão), usa a logo escura (lightSrc)
            logo.src = isDarkMode ? darkSrc : lightSrc;
        }
        
        // Se a regra de fill/stroke do SVG for necessária para outros SVGs no futuro:
        // Se a logo for do cabeçalho, a cor é controlada pelo fill/stroke no CSS (se não for image tag)
        // Se a logo for do body, a cor é controlada pelo fill/stroke no CSS
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('theme-toggle');
    const body = document.body;
    const sunIcon = toggleButton.querySelector('.fa-sun');
    const moonIcon = toggleButton.querySelector('.fa-moon');

    // 1. Verifica se há uma preferência de tema salva no armazenamento local
    const savedTheme = localStorage.getItem('theme');

    let isInitialDark = false;

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

    updateLogoSource(isInitialDark);

    // 2. Adiciona o listener para alternar o tema ao clicar
    toggleButton.addEventListener('click', () => {
        
        // Alterna a classe 'dark-mode' no corpo do documento
        body.classList.toggle('dark-mode');
        
        // 🚨 CORREÇÃO: Define a variável com o NOVO estado do body
        const isCurrentlyDark = body.classList.contains('dark-mode'); 

        // Salva a nova preferência no armazenamento local
        if (isCurrentlyDark) { // Usa a variável corrigida
            localStorage.setItem('theme', 'dark');
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline';
        } else {
            localStorage.setItem('theme', 'light');
            sunIcon.style.display = 'inline';
            moonIcon.style.display = 'none';
        }

        // 🚨 CHAMADA NO CLIQUE: Usa a variável corrigida
        updateLogoSource(isCurrentlyDark);
    });

    const sidebarToggle = document.getElementById('sidebar-toggle');
    const overlay = document.querySelector('.overlay'); 
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            // Alterna a classe 'sidebar-active' no corpo do documento
            body.classList.toggle('sidebar-active');
        });

        if (overlay) {
            overlay.addEventListener('click', () => {
                // Remove a classe 'sidebar-active' do corpo
                body.classList.remove('sidebar-active'); 
            });
        }
        
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