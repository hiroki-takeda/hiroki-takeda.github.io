window.addEventListener('DOMContentLoaded', () => {
    const insertHTML = (selector, url) => {
      fetch(url)
        .then(res => res.text())
        .then(data => {
          document.querySelector(selector).innerHTML = data;
        });
    };
  
    insertHTML('#header-placeholder', 'header.html');
    insertHTML('#footer-placeholder', 'footer.html');
  });
   