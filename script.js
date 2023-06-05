window.addEventListener('DOMContentLoaded', (event) => {
    const navIcon = document.getElementById('nav-icon');
    const navMenu = document.getElementById('nav-menu');

    // 画面の幅に基づいて、ナビゲーションメニューの表示を制御します。
    function adjustMenu() {
        if (window.innerWidth <= 480) {
           navMenu.style.display = "flex";
            navIcon.style.display = "none";
        } else if (window.innerWidth <= 874) {
            navMenu.style.display = "none";
            navIcon.style.display = "flex";
        } else {
            navMenu.style.display = "flex";
            navIcon.style.display = "none";
        }
    }

    // 初回ページ読み込み時にメニュー表示を調整します。
    adjustMenu();

    // ハンバーガーアイコンをクリックしたときのイベントを設定します。
    navIcon.addEventListener('click', function() {
        if (navMenu.style.display === 'none') {
            navMenu.style.display = 'flex';
        } else {
            navMenu.style.display = 'none';
        }
    });

    // ウィンドウサイズの変更を検知して、メニュー表示を調整します。
    window.addEventListener('resize', adjustMenu);
});
