(function () {
  var acct = document.getElementById('acct');
  var btn = document.getElementById('acctBtn');
  if (!acct || !btn) return;

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    var open = acct.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
  });
  document.addEventListener('click', function (e) {
    if (!acct.contains(e.target)) acct.classList.remove('open');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') acct.classList.remove('open');
  });
})();