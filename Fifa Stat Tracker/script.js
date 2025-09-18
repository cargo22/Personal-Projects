// retreiving certain items we need
const start = document.getElementById("start-button");
const initial_screen = document.getElementById("start-screen");
const setup_screen = document.getElementById("setup-screen");
const players_select = document.getElementById("num-players");
const advance = document.getElementById("advance-button");
const contestants_screen = document.getElementById("contestants");
const tournament_hub = document.getElementById("tournament-hub");
const names = document.getElementById("submit-names");
const matches_screen = document.getElementById("matches");
const games = document.getElementById("games");
const results_button = document.getElementById("results-button");

// when commencing the tournament, we want to go to the next 'page'
start.addEventListener("click", () => {
    initial_screen.style.display = "none";
    setup_screen.style.display = "flex";
});

// assigning the number of players to the dropdown value
let num_players = players_select.value;

// whenever you change the dropdown value, the value of num_players changes
players_select.addEventListener('change', function() {
    num_players = this.value;
});

// when selecting the number of players, we want to go to the next 'page' prompting to enter contestant names
advance.addEventListener("click", () => {
    setup_screen.style.display = "none";
    contestants_screen.style.display = "flex";

    namesForm.innerHTML = '';

    // creating an input for each player that was indicated
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

// storing the names in a list
let player_names = [];

// once all names are entered, we want to store them and display all possible matchups
names.addEventListener('click', (e) => {
    e.preventDefault();

    // moving to next page, firstly
    contestants_screen.style.display = "none";
    matches_screen.style.display = "flex";

    // retreiving the inputs
    const inputs = namesForm.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        player_names.push(input.value.trim()); 
    });

    // generating the possible matches
    const matches = [];
    for (let i = 0; i < player_names.length; i++) {
        for (let j = i + 1; j < player_names.length; j++) {
            matches.push([player_names[i], player_names[j]]);
        }
    }

    games.innerHTML = ''; 

    // for each match, we will create a div that has the names of the players in the match as well as an input to track what the score is
    matches.forEach((match, index) => {
        const div = document.createElement('div');
        div.className = "game";

        // creating the layoug
        div.innerHTML = `
            <span class="player">${match[0]}</span>
            <input type='number' min='0' class='score' id='score_${index}_1' placeholder="score">
            <span class="vs">vs</span>
            <input type='number' min='0' class='score' id='score_${index}_2' placeholder="score">
            <span class="player">${match[1]}</span>
        `;

        games.appendChild(div);
    });
});

// now that we have entered all the matches, we want to create the resulting table
const table = document.createElement("div");
tournament_hub.appendChild(table);

// once we press the button that confirms the scores, we want our table to appear
results_button.addEventListener("click", () => {
    matches_screen.style.display = "none";
    tournament_hub.style.display = "flex";

    // creating base standings
    let standings = {};
    player_names.forEach(name => {
        standings[name] = {points: 0, gf: 0, ga: 0, gd: 0};
    });

    // re-entering the possible matchups
    const matches = [];
    for (let i = 0; i < player_names.length; i++) {
        for (let j = i + 1; j < player_names.length; j++){
            matches.push([player_names[i], player_names[j]]);
        }
    }

    // for each matchup, we want to retreive the score
    matches.forEach((match, index) => {
        const p1 = match[0];
        const p2 = match[1];

        // getting the score
        const score1 = parseInt(document.getElementById(`score_${index}_1`).value) || 0;
        const score2 = parseInt(document.getElementById(`score_${index}_2`).value) || 0;

        // updating goals for and goals against
        standings[p1].gf += score1;
        standings[p1].ga += score2;
        standings[p2].gf += score2;
        standings[p2].ga += score1;

        // keeping track of the goal difference
        standings[p1].gd = standings[p1].gf - standings[p1].ga;
        standings[p2].gd = standings[p2].gf - standings[p2].ga;

        // assigning points accordingly
        if (score1 > score2) {
            standings[p1].points += 3;
        } else if (score2 > score1) {
            standings[p2].points += 3;
        } else {
            standings[p1].points += 1;
            standings[p2].points += 1;
        }
    });

    // converting into array
    let tableData = Object.entries(standings).map(([name, stats]) => ({
        name,
        ...stats
    }));

    // sorting by points, then goal difference, then goals for
    tableData.sort((a, b) => 
        b.points - a.points ||
        b.gd - a.gd ||
        b.gf - a.gf
    );

    // making the table
    let html = `
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Player</th>
                <th>Points</th>
                <th>GF</th>
                <th>GA</th>
                <th>GD</th>
            </tr>
    `;
    tableData.forEach(row => {
        html += `
            <tr>
                <td>${row.name}</td>
                <td>${row.points}</td>
                <td>${row.gf}</td>
                <td>${row.ga}</td>
                <td>${row.gd}</td>
            </tr>
        `;
    });
    html += `</table>`;

    table.innerHTML = html;
});