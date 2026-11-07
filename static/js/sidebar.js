(function () {
  var root = document.documentElement;
  var app = document.getElementById('app');
  if (!app) return;

  var small = window.matchMedia('(max-width: 900px)');
  var collapseBtn = document.getElementById('collapseBtn');
  var menuBtn = document.getElementById('menuBtn');
  var backdrop = document.getElementById('backdrop');
  var acct = document.getElementById('acct');
  var acctBtn = document.getElementById('acctBtn');

  function toggleCollapse() {
    var collapsed = root.getAttribute('data-side') === 'collapsed';
    if (collapsed) root.removeAttribute('data-side');
    else root.setAttribute('data-side', 'collapsed');
    try { localStorage.setItem('kb-side', collapsed ? '0' : '1'); } catch (e) {}
  }
  function setMobile(open) { app.classList.toggle('side-open', open); }

  if (collapseBtn) collapseBtn.addEventListener('click', toggleCollapse);
  if (menuBtn) menuBtn.addEventListener('click', function () {
    if (small.matches) setMobile(!app.classList.contains('side-open'));
    else toggleCollapse();
  });
  if (backdrop) backdrop.addEventListener('click', function () { setMobile(false); });

  if (acct && acctBtn) {
    acctBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = acct.classList.toggle('open');
      acctBtn.setAttribute('aria-expanded', open);
    });
    document.addEventListener('click', function (e) {
      if (!acct.contains(e.target)) acct.classList.remove('open');
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { setMobile(false); if (acct) acct.classList.remove('open'); }
  });
})();