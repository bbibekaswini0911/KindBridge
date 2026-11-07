(function () {
  var input = document.querySelector('input[type=file]');
  var box = document.getElementById('preview');
  if (!input || !box) return;

  input.addEventListener('change', function () {
    box.innerHTML = '';
    var files = Array.prototype.slice.call(input.files, 0, 3);
    files.forEach(function (f) {
      if (!/^image\//.test(f.type)) return;
      var img = document.createElement('img');
      img.src = URL.createObjectURL(f);
      img.alt = f.name;
      box.appendChild(img);
    });
    if (input.files.length > 3) {
      var p = document.createElement('p');
      p.className = 'err';
      p.textContent = 'Please choose at most 3 photos.';
      box.appendChild(p);
    }
  });
})();
