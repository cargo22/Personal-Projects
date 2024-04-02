document.addEventListener('DOMContentLoaded', () => {
    // creating the container object
    const puzzleContainer = document.getElementById('puzzleContainer');
    const puzzlePieces = [];
    const clickedPieces = [];

    if (puzzleContainer) {
        // creating the 3x3 grid with a for loop
        for (let i = 1; i <= 9; i++) {
            // distinguishing each piece
            const puzzlePiece = document.createElement('div');
            puzzlePiece.className = 'puzzle-piece';
            puzzlePiece.dataset.number = i;
            puzzlePiece.innerText = i;

            // adding necessary values and setting click events
            puzzlePiece.addEventListener('click', () => onPuzzlePieceClick(i));
            puzzlePieces.push(puzzlePiece);
            puzzleContainer.appendChild(puzzlePiece);
        }
    }

    // function to handle puzzle piece clicks
    const onPuzzlePieceClick = (clickedNumber) => {
        const currentPiece = puzzlePieces[clickedNumber - 1];

        // Check if the current puzzle piece is clickable
        if (isClickable(clickedNumber)) {
            // Perform your logic for each puzzle level
            switch (clickedNumber) {
                case 1:
                    // Redirect to the first riddle question
                    const answer1 = prompt("What has to be broken before you can use it?")
                    checkAnswer1(answer1);
                    break;
                case 2:
                    const answer2 = prompt("What is always in front of you but can’t be seen?");
                    checkAnswer2(answer2);
                    break;
                // Add more cases for each puzzle level
                case 3:
                    const answer3 = prompt("What goes up but never comes down?")
                    checkAnswer3(answer3);
                    break;
                // Example for the last puzzle piece
                case 4:
                    const answer4 = prompt("What gets wet while drying?")
                    checkAnswer4(answer4);
                    break;
                case 5:
                    const answer5 = prompt("I follow you all the time and copy your every move, but you can’t touch me or catch me. What am I?");
                    checkAnswer5(answer5);
                    break;
                case 6:
                    const answer6 = prompt("I am an odd number. Take away a letter and I become even. What number am I?");
                    checkAnswer6(answer6);
                    break;
                case 7:
                    const answer7 = prompt("Spelled forwards I’m what you do every day, spelled backward I’m something you hate. What am I?");
                    checkAnswer7(answer7);
                    break;
                case 8:
                    const answer8 = prompt("What belongs to you, but everyone else uses it.");
                    checkAnswer8(answer8);
                    break;
                case 9:
                    window.location.href = 'riddle1.html';
                    break;
                default:
                    // Default case for levels that don't require a riddle
                    alert(`Move on to the next puzzle.`);
                    break;
            }

            // Add additional logic or UI changes as needed
            currentPiece.classList.add('clicked'); // Add the 'clicked' class
        } else {
            // Puzzle piece is not clickable yet, inform the user
            alert('Solve the previous puzzle to unlock this one!');
        }
    };

    // Function to check if the puzzle piece is clickable
    const isClickable = (clickedNumber) => {
        return clickedPieces.includes(clickedNumber) || clickedNumber <= 1;
    };

    function checkAnswer1(answer) {
        // Compare user's answer with the correct answer
        if (answer.toLowerCase() === 'egg' || answer.toLowerCase() === 'an egg') {
            alert('Correct! You can move on to the next puzzle.');
            clickedPieces.push(2);
            console.log(clickedPieces);
        } else {
            alert('Incorrect! Try again.');
        }
    }

    function checkAnswer2(answer) {
        if (answer.toLowerCase() === 'the future' || answer.toLowerCase() === 'future') {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(3);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer3(answer) {
        if (answer.toLowerCase().includes('age')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(4);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer4(answer) {
        if (answer.toLowerCase().includes('towel')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(5);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer5(answer) {
        if (answer.toLowerCase().includes('shadow')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(6);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer6(answer) {
        if (answer.toLowerCase().includes('seven')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(7);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer7(answer) {
        if (answer.toLowerCase().includes('live')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(8);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    function checkAnswer8(answer) {
        if (answer.toLowerCase().includes('name')) {
            alert('Correct! You can move on to the next puzzle');
            clickedPieces.push(9);
        } else {
            alert('Incorrect! Try again.')
        }
    }

    const readyButton = document.getElementById('final_button');
    if (readyButton) {
        readyButton.addEventListener('click', () => {
            window.location.href = 'final_decision.html';
        })
    }

    const noButton = document.getElementById('no_btn');
    const message = document.getElementById('incorrect_message');
    if (noButton) {
        // Add a hover event listener to the "No" button
        noButton.addEventListener('mouseover', function () {
            // Add a class to the body to change the background color
            document.body.classList.add('dark-background');
            message.textContent = 'That is incorrect, madame.'
        });

        // Add a mouseout event listener to revert the background color
        noButton.addEventListener('mouseout', function () {
            // Remove the class to revert the background color
            document.body.classList.remove('dark-background');
            message.textContent = '';
        });
    }

    const yesButton = document.getElementById('yes_btn');
    if (yesButton) {
        yesButton.addEventListener('click', function () {
            window.location.href = 'yipee.html';
        })
    }
});
