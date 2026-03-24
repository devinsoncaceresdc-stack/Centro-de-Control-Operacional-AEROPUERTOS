// Animación simple al cargar
document.addEventListener("DOMContentLoaded", function() {
    console.log("Dashboard Aeropuerto cargado ✈️");

    const title = document.querySelector("h1");

    if (title) {
        title.style.transition = "0.5s";
        title.onmouseover = () => {
            title.style.color = "#00ffcc";
        };
        title.onmouseout = () => {
            title.style.color = "#00d4ff";
        };
    }
});