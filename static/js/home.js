(function () {
  /* rotating headline */
  var rot = document.getElementById('rot');
  var lead = document.getElementById('lead');
  if (rot && lead) {
    var phrases = ['to an orphanage near you', 'to an old age home', 'to a care center', 'and track every request'];
    var lines = [
      'See exactly what each home needs, donate the items, and follow your request until it is approved.',
      'Elders need medicine, warm clothes and company. Pick what you can give.',
      'Care centers post their needs. You choose the center and the items.',
      'Pending, Approved or Rejected. You always know where your donation stands.'
    ];
    var i = 1, typer;
    setInterval(function () {
      clearInterval(typer);
      var k = (i % 5) + 1;
      var text = phrases[i % phrases.length];
      rot.className = 'rot';
      void rot.offsetWidth;
      if (k === 4) {
        rot.textContent = '';
        rot.classList.add('a4');
        var j = 0;
        typer = setInterval(function () {
          rot.textContent = text.slice(0, ++j);
          if (j >= text.length) {clearInterval(typer); rot.classList.remove('a4');}
        }, 45);
      } else {
        rot.textContent = text;
        rot.classList.add('a' + k);
      }
      lead.style.opacity = 0;
      setTimeout(function () {
        lead.textContent = lines[i % lines.length];
        lead.style.opacity = 1;
        i++;
      }, 250);
    }, 4200);
  }

  /* counters */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var el = e.target, n = +el.dataset.n, start = performance.now();
      (function tick(t) {
        var p = Math.min((t - start) / 1200, 1);
        el.textContent = Math.round(n * p).toLocaleString('en-IN');
        if (p < 1) requestAnimationFrame(tick);
      })(start);
    });
  }, { threshold: 0.4 });
  document.querySelectorAll('[data-n]').forEach(function (el) { io.observe(el); });

  /* FAQ tabs */
  var tabBtns = document.querySelectorAll('.tabs button');
  tabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      tabBtns.forEach(function (b) { b.classList.remove('on'); });
      document.querySelectorAll('.panel').forEach(function (p) { p.classList.remove('on'); });
      btn.classList.add('on');
      document.getElementById('tab-' + btn.dataset.tab).classList.add('on');
    });
  });

  /* endless scrolling rows: duplicate the content once */
  document.querySelectorAll('.marquee-track').forEach(function (track) {
    Array.from(track.children).forEach(function (child) {
      track.appendChild(child.cloneNode(true));
    });
  });

  /* contact form: front-end only for now, shows a pop-up */
  var form = document.getElementById('contactForm');
  var area = document.getElementById('toastArea');
  if (form && area) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var t = document.createElement('div');
      t.className = 'toast success';
      t.innerHTML = '<span>Thanks, your message was noted.</span><button type="button" class="toast-close" aria-label="Close">&times;</button>';
      area.appendChild(t);
      function hide() { t.classList.add('hide'); setTimeout(function () { t.remove(); }, 300); }
      t.querySelector('.toast-close').addEventListener('click', hide);
      setTimeout(hide, 4000);
      form.reset();
    });
  }
})();