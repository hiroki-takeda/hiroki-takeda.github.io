window.addEventListener('DOMContentLoaded', () => {
  const insertHTML = (selector, url) => {
    return fetch(url)
      .then(res => res.text())
      .then(data => {
        document.querySelector(selector).innerHTML = data;
      });
  };

  Promise.all([
    insertHTML('#header-placeholder', 'header.html'),
    insertHTML('#footer-placeholder', 'footer.html')
  ]).then(() => {
    // ✅ header/footer 挿入後に初めて nav を取得・制御
    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');

    function adjustMenu() {
      if (window.innerWidth <= 768) {
        navIcon.style.display = 'flex';
        navMenu.classList.remove('active');
      } else {
        navIcon.style.display = 'none';
        navMenu.classList.add('active');
      }
    }

    adjustMenu();

    navIcon.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });

    window.addEventListener('resize', adjustMenu);
  });
});
