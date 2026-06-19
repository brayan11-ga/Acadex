const menuBtn = document.querySelector(".menu-toggle");
const mobileMenu = document.querySelector(".mobile-menu");

menuBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("active");
});

// Cerrar al seleccionar una opción
const menuLinks = document.querySelectorAll(".mobile-menu a");

menuLinks.forEach(link => {
    link.addEventListener("click", () => {
        mobileMenu.classList.remove("active");
    });
});

// Cerrar al hacer click fuera del menú
document.addEventListener("click", (e) => {

    const clickDentroDelMenu = mobileMenu.contains(e.target);
    const clickEnBoton = menuBtn.contains(e.target);

    if (!clickDentroDelMenu && !clickEnBoton) {
        mobileMenu.classList.remove("active");
    }

});