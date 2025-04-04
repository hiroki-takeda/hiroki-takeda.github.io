window.addEventListener('DOMContentLoaded', (event) => {
    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');
  
    function adjustMenu() {
      if (window.innerWidth <= 874) {
        navMenu.classList.remove('active');
        navMenu.style.display = "none";  // 初期状態
        navIcon.style.display = "flex";
      } else {
        navMenu.style.display = "flex";
        navIcon.style.display = "none";
      }
    }
  
    adjustMenu();
  
    navIcon.addEventListener('click', function () {
      navMenu.classList.toggle('active');
    });
  
    window.addEventListener('resize', adjustMenu);
  });