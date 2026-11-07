document.querySelectorAll('.toast').forEach(function (toast) {
    function hide() {
    toast.classList.add('hide');
    setTimeout(function () { toast.remove(); }, 300);
    }
    toast.querySelector('.toast-close').addEventListener('click', hide);
    setTimeout(hide, 4500);
});