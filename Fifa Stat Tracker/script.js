const start = document.querySelector("#start-button")
const initial_screen = document.querySelector("#start-screen")
const hub = document.querySelector("#tournament-hub")

start.addEventListener("click", () => {
    initial_screen.style.display = "none";
    hub.style.display = "block";
});