(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Draggable contact button ---------- */
  var fab = document.getElementById('fab');
  var btn = document.getElementById('fabBtn');

  if (fab && btn) {
    var drag = null, moved = false;

    /* open the panel towards the side that has room */
    function place() {
      var r = fab.getBoundingClientRect();
      fab.classList.toggle('down', r.top < 300);
      fab.classList.toggle('left', r.left < 300);
    }
    function closePanel() {
      fab.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }

    btn.addEventListener('pointerdown', function (e) {
      var r = fab.getBoundingClientRect();
      drag = { dx: e.clientX - r.left, dy: e.clientY - r.top, x: e.clientX, y: e.clientY };
      moved = false;
      btn.setPointerCapture(e.pointerId);
    });

    btn.addEventListener('pointermove', function (e) {
      if (!drag) return;
      if (!moved) {
        if (Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) < 6) return;
        moved = true;
        fab.classList.add('dragging');
        closePanel();
      }
      var x = Math.min(Math.max(8, e.clientX - drag.dx), window.innerWidth - fab.offsetWidth - 8);
      var y = Math.min(Math.max(8, e.clientY - drag.dy), window.innerHeight - fab.offsetHeight - 8);
      fab.style.left = x + 'px';
      fab.style.top = y + 'px';
      fab.style.right = 'auto';
      fab.style.bottom = 'auto';
    });

    function endDrag() {
      if (!drag) return;
      drag = null;
      fab.classList.remove('dragging');
      place();
    }
    btn.addEventListener('pointerup', endDrag);
    btn.addEventListener('pointercancel', endDrag);

    btn.addEventListener('click', function () {
      if (moved) { moved = false; return; }   /* it was a drag, not a click */
      place();
      var open = fab.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });

    document.addEventListener('click', function (e) {
      if (!fab.contains(e.target)) closePanel();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closePanel();
    });
    document.getElementById('fabGo').addEventListener('click', closePanel);

    /* keep the button on screen if the window gets smaller */
    window.addEventListener('resize', function () {
      if (!fab.style.left) return;
      var x = Math.min(parseFloat(fab.style.left), window.innerWidth - fab.offsetWidth - 8);
      var y = Math.min(parseFloat(fab.style.top), window.innerHeight - fab.offsetHeight - 8);
      fab.style.left = Math.max(8, x) + 'px';
      fab.style.top = Math.max(8, y) + 'px';
    });
  }

  /* ---------- Hero: mouse glow and card tilt ---------- */
  var hero = document.querySelector('.hero');
  var card = document.querySelector('.search-card');
  if (hero && !reduce && window.matchMedia('(hover: hover)').matches) {
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      hero.style.setProperty('--mx', x + 'px');
      hero.style.setProperty('--my', y + 'px');
      if (card) {
        var px = x / r.width - 0.5, py = y / r.height - 0.5;
        card.style.transform = 'rotateY(' + (px * 6) + 'deg) rotateX(' + (-py * 6) + 'deg)';
      }
    });
    hero.addEventListener('mouseleave', function () {
      if (card) card.style.transform = '';
    });
  }
})();