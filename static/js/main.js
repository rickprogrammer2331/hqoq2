AOS.init({
    duration: 1000,
    once: true
});

const menuBtn = document.querySelector('.mobile-menu-btn');
const navMenu = document.querySelector('nav ul');
const searchContainer = document.querySelector('.search-container');
let isSearchVisible = false;

if (menuBtn && navMenu) {
    menuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        
        if (isSearchVisible && window.innerWidth <= 768) {
            searchContainer.classList.remove('show');
            isSearchVisible = false;
        }
        
        navMenu.classList.toggle('show');
        menuBtn.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!navMenu.contains(e.target) && !menuBtn.contains(e.target)) {
            if (navMenu.classList.contains('show')) {
                navMenu.classList.remove('show');
                menuBtn.classList.remove('active');
            }
            if (isSearchVisible && !searchContainer.contains(e.target)) {
                searchContainer.classList.remove('show');
                isSearchVisible = false;
            }
        }
    });

    navMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
}

const searchButton = document.getElementById('searchButton');
const searchInput = document.getElementById('searchInput');

searchButton.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
        e.preventDefault();
        e.stopPropagation();
        
        isSearchVisible = !isSearchVisible;
        searchContainer.classList.toggle('show');
        
        if (isSearchVisible) {
            navMenu.classList.remove('show');
            menuBtn.classList.remove('active');
            searchInput.focus();
        }
    } else {
        performSearch();
    }
});

searchContainer.addEventListener('click', function(e) {
    e.stopPropagation();
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('show');
                menuBtn.classList.remove('active');
            }
            
            window.scrollTo({
                top: target.offsetTop - 60, 
                behavior: 'smooth'
            });
        }
    });
});

function performSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    if (!searchTerm) return;

    const sections = document.querySelectorAll('section');
    let found = false;
    
    sections.forEach(section => {
        const content = section.textContent.toLowerCase();
        if (content.includes(searchTerm)) {
            if (window.innerWidth <= 768) {
                navMenu.classList.remove('show');
                menuBtn.classList.remove('active');
                searchContainer.classList.remove('show');
                isSearchVisible = false;
            }
            
            section.scrollIntoView({ behavior: 'smooth' });
            section.style.animation = 'highlight 2s';
            found = true;
            return;
        }
    });

    if (!found) {
        alert('لم يتم العثور على نتائج');
    }
}

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        navMenu.classList.remove('show');
        menuBtn.classList.remove('active');
        searchContainer.classList.remove('show');
        isSearchVisible = false;
    }
});

const style = document.createElement('style');
style.textContent = `
@keyframes highlight {
    0% { background-color: rgba(193, 120, 23, 0.2); }
    100% { background-color: transparent; }
}`;
document.head.appendChild(style);