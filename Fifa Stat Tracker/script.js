const start = document.getElementById("start-button");
const initial_screen = document.getElementById("start-screen");
const setup_screen = document.getElementById("setup-screen");
const players_select = document.getElementById("num-players");
const advance = document.getElementById("advance-button");
const contestants_screen = document.getElementById("contestants");
const tournament_hub = document.getElementById("tournament-hub");
const names = document.getElementById("submit-names");
const results = document.getElementById("matches");

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

let player_names = [];

names.addEventListener('click', (e) => {
    e.preventDefault();

    player_names = [];

    contestants_screen.style.display = "none";
    results.style.display = "flex";

    const inputs = namesForm.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        player_names.push(input.value.trim()); 
    });

    console.log(player_names);
    // Generate matches here
    const matches = [];
    for (let i = 0; i < player_names.length; i++) {
        for (let j = i + 1; j < player_names.length; j++) {
            matches.push([player_names[i], player_names[j]]);
        }
    }

    // Render matches
    results.innerHTML = '';
    matches.forEach((match, index) => {
        const div = document.createElement('div');
        div.className = "game";

        div.innerHTML = `
            <span>${match[0]}</span>
            <input type='number' min='0' class='score' id='score_${index}_1' placeholder="score">
            <span>vs</span>
            <input type='number' min='0' class='score' id='score_${index}_2' placeholder="score">
            <span>${match[1]}</span>
        `;

        results.appendChild(div);
    });
});
