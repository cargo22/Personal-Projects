const start = document.getElementById("start-button");
const initial_screen = document.getElementById("start-screen");
const setup_screen = document.getElementById("setup-screen");

start.addEventListener("click", () => {
    initial_screen.style.display = "none";
    setup_screen.style.display = "flex";
});