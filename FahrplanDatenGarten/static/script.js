// Navbar Toogle
var navbar_burger = document.getElementsByClassName('navbar-burger')[0]
navbar_burger.addEventListener('click', () => {
    const target = navbar_burger.dataset.target;
    const $target = document.getElementById(target);

    navbar_burger.classList.toggle('is-active');
    $target.classList.toggle('is-active');
});