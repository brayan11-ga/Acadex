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


function initHeroParticles() {

    const hero = document.querySelector(".hero");
    const canvas = document.getElementById("heroParticles");

    if (!hero || !canvas) return;

    (() => {
    const hero = document.querySelector('.hero');
    const canvas = document.getElementById('heroParticles');

    if (!hero || !canvas) return;

    const ctx = canvas.getContext('2d');
    const state = {
        width: 0,
        height: 0,
        dpr: Math.max(1, window.devicePixelRatio || 1),
        mouseX: 0,
        mouseY: 0,
        targetX: 0,
        targetY: 0,
        active: false,
        dots: []
    };

    const spacing = 22;          // distancia entre pepitas
    const influenceRadius = 180; // área de reacción del mouse

    function resize() {
        const rect = hero.getBoundingClientRect();

        state.width = rect.width;
        state.height = rect.height;

        canvas.width = Math.floor(rect.width * state.dpr);
        canvas.height = Math.floor(rect.height * state.dpr);
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;

        ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);

        state.dots = [];

        for (let y = spacing / 2; y < state.height; y += spacing) {
            for (let x = spacing / 2; x < state.width; x += spacing) {
                state.dots.push({
                    x,
                    y,
                    baseSize: 0.9 + Math.random() * 0.7,
                    drift: Math.random() * Math.PI * 2
                });
            }
        }
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function draw(time) {
        ctx.clearRect(0, 0, state.width, state.height);

        // Suavizado del mouse
        state.mouseX = lerp(state.mouseX, state.targetX, 0.08);
        state.mouseY = lerp(state.mouseY, state.targetY, 0.08);

        // Brillo suave alrededor del mouse
        if (state.active) {
            const glow = ctx.createRadialGradient(
                state.mouseX,
                state.mouseY,
                0,
                state.mouseX,
                state.mouseY,
                influenceRadius
            );
            glow.addColorStop(0, 'rgba(111, 154, 253, 0.10)');
            glow.addColorStop(0.4, 'rgba(78, 222, 163, 0.06)');
            glow.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.fillStyle = glow;
            ctx.fillRect(0, 0, state.width, state.height);
        }

        for (const dot of state.dots) {
            const dx = dot.x - state.mouseX;
            const dy = dot.y - state.mouseY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            const influence = state.active
                ? Math.max(0, 1 - dist / influenceRadius)
                : 0;

            const pulse = Math.sin(time * 0.0015 + dot.drift) * 0.25 + 0.75;
            const size = dot.baseSize + influence * 1.8 + pulse * 0.25;

            // Color base + color reactivo al mouse
            const r = Math.round(lerp(62, 111, influence));
            const g = Math.round(lerp(190, 154, influence));
            const b = Math.round(lerp(255, 253, influence));
            const alpha = 0.18 + influence * 0.55;

            ctx.beginPath();
            ctx.arc(dot.x, dot.y, size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
            ctx.fill();
        }

        requestAnimationFrame(draw);
    }

    hero.addEventListener('mousemove', (e) => {
        const rect = hero.getBoundingClientRect();
        state.targetX = e.clientX - rect.left;
        state.targetY = e.clientY - rect.top;
        state.active = true;
    });

    hero.addEventListener('mouseleave', () => {
        state.active = false;
        state.targetX = state.width / 2;
        state.targetY = state.height / 2;
    });

    window.addEventListener('resize', resize);

    resize();
    state.targetX = state.width / 2;
    state.targetY = state.height / 2;
    state.mouseX = state.targetX;
    state.mouseY = state.targetY;

    requestAnimationFrame(draw);
})();
}

document.addEventListener("DOMContentLoaded", () => {

    // Menú móvil
    // ...

    // Animaciones del hero
    initHeroParticles();

});