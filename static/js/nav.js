(function () {
    var btn = document.getElementById('navToggle');
    var nav = document.getElementById('mainNav');
    if (!btn || !nav) return;

    btn.addEventListener('click', function () {
        var open = nav.classList.toggle('open');
        btn.classList.toggle('on', open);
        btn.setAttribute('aria-expanded', open);
    });

    var mega = nav.querySelector('.has-mega');
    var megaBtn = nav.querySelector('.mega-btn');
    if (mega && megaBtn) {
        megaBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = mega.classList.toggle('open');
        megaBtn.setAttribute('aria-expanded', open);
        });
        document.addEventListener('click', function (e) {
        if (!mega.contains(e.target)) mega.classList.remove('open');
        });
    }

    nav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
        nav.classList.remove('open');
        btn.classList.remove('on');
        if (mega) mega.classList.remove('open');
        });
    });
})();