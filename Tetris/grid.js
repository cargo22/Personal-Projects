const grid = document.querySelector('.grid');

let htmlString = "";


for (let i = 1; i <= 200; i += 1) {
    htmlString += `<div></div>`;    
}

grid.innerHTML = htmlString;