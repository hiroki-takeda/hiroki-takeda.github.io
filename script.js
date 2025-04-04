window.addEventListener('DOMContentLoaded', () => {
    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');
  
    function adjustMenu() {
      if (window.innerWidth <= 768) {
        navMenu.classList.remove('active');
        navIcon.style.display = 'flex';
      } else {
        navMenu.classList.add('active');
        navIcon.style.display = 'none';
      }
    }
  
    adjustMenu();
  
    navIcon.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  
    window.addEventListener('resize', adjustMenu);
  });
  