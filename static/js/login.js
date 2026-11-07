(function () {
  var input = document.getElementById('roleInput');
  if (!input) return;
  var tabs = document.querySelectorAll('.role-toggle button');
  var sub = document.getElementById('loginSub');
  var reg = document.getElementById('regLink');
  var texts = {
    donor: 'Log in to donate and track your requests.',
    center: 'Log in to manage your requests and see what donors offer.'
  };
  var labels = { donor: 'Create a donor account', center: 'Register your care center' };

  function setRole(role) {
    input.value = role;
    tabs.forEach(function (t) {
      var on = t.dataset.role === role;
      t.classList.toggle('on', on);
      t.setAttribute('aria-selected', on);
    });
    sub.textContent = texts[role];
    reg.href = reg.dataset[role];
    reg.textContent = labels[role];
  }
  tabs.forEach(function (t) {
    t.addEventListener('click', function () { setRole(t.dataset.role); });
  });
  setRole(input.value === 'center' ? 'center' : 'donor');
})();