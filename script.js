window.onload = function() {
  var navIcon = document.getElementById('nav-icon');
  var navMenu = document.getElementById('nav-menu');

  navIcon.onclick = function() {
    navMenu.classList.toggle('active');
  }

　window.onresize = function() {
    if (window.innerWidth > 800) {
        navMenu.style.display = '';
        navMenu.classList.remove('active');
    } else if (!navMenu.classList.contains('active')) {
        navMenu.style.display = '';
    }
  }
}