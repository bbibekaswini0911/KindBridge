(function () {
  var main = document.getElementById('mainImg');
  if (!main) return;
  document.querySelectorAll('.thumbs img').forEach(function (thumb) {
    thumb.addEventListener('click', function () { main.src = thumb.dataset.full; });
  });
})();