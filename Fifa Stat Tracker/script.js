const start = document.getElementById("start-button");
const initial_screen = document.getElementById("start-screen");
const setup_screen = document.getElementById("setup-screen");
const players_select = document.getElementById("num-players");
const advance = document.getElementById("advance-button");
const tournament_hub = document.getElementById("tournament-hub");

start.addEventListener("click", () => {
    initial_screen.style.display = "none";
    setup_screen.style.display = "flex";
});

let num_players = players_select.value;

players_select.addEventListener('change', function() {
    num_players = this.value;
});

advance.addEventListener("click", () => {
    setup_screen.style.display = "none";
    tournament_hub.style.display = "flex";
});
