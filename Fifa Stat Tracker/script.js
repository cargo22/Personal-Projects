const start = document.getElementById("start-button");
const initial_screen = document.getElementById("start-screen");
const setup_screen = document.getElementById("setup-screen");
const players_select = document.getElementById("num-players");
const advance = document.getElementById("advance-button");
const contestants_screen = document.getElementById("contestants");
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
    contestants_screen.style.display = "flex";

    namesForm.innerHTML = '';

    for (let i = 1; i <= num_players; i++) {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = `player${i}`;
        input.placeholder = `Player ${i} name`;
        input.required = true;
        namesForm.appendChild(input);
        namesForm.appendChild(document.createElement('br'));
    }
});
