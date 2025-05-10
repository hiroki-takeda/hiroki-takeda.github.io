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
    // ✅ header/footer の挿入後に script.js 相当の処理を書く

    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');
    const navClose = document.getElementById('nav-close'); // ← 追加

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

  if (navClose) {
    navClose.addEventListener('click', () => {
    navMenu.classList.remove('active');
    });
  }

    window.addEventListener('resize', adjustMenu);
  });
});
