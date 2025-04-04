window.addEventListener('DOMContentLoaded', () => {
    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');
  
    function adjustMenu() {
      if (window.innerWidth <= 768) {
        navIcon.style.display = 'flex';
        navMenu.classList.remove('active'); // ← 非表示に
      } else {
        navIcon.style.display = 'none';
        navMenu.classList.add('active'); // ← 常時表示
      }
    }
  
    adjustMenu();
  
    navIcon.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  
    window.addEventListener('resize', adjustMenu);
  });
  