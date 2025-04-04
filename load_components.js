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
    // header/footer の挿入が完了した後に script.js を実行
    const script = document.createElement('script');
    script.src = 'script.js';
    document.body.appendChild(script);
  });
});