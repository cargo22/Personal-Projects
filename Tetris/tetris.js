document.addEventListener('DOMContentLoaded', () => {
  // necessary variables 
  // ------------------------------------------------------------------------------------------------
  const grid = document.querySelector('.grid')
  let squares = Array.from(document.querySelectorAll('.grid div'))
  const scoreDisplay = document.querySelector('#score')
  const startButton = document.querySelector('#startButton')
  let nextRandom = 0
  const width = 10
  let timerID
  let score = 0
  const colors = [
    'orange',
    'red',
    'purple',
    'green',
    'blue'
  ]

  // drawing the blocks
  // ------------------------------------------------------------------------------------------------
  const lBlock = [
    [1, width + 1, width * 2 + 1, 2],
    [width, width + 1, width + 2, width * 2 + 2],
    [1, width + 1, width * 2 + 1, width * 2],
    [width, width * 2, width * 2 + 1, width * 2 + 2]
  ]
  const zBlock = [
    [0, width, width + 1, width * 2 + 1],
    [width + 1, width + 2, width * 2, width * 2 + 1],
    [0, width, width + 1, width * 2 + 1],
    [width + 1, width + 2, width * 2, width * 2 + 1]
  ]

  const tBlock = [
    [1, width, width + 1, width + 2],
    [1, width + 1, width + 2, width * 2 + 1],
    [width, width + 1, width + 2, width * 2 + 1],
    [1, width, width + 1, width * 2 + 1]
  ]

  const oBlock = [
    [0, 1, width, width + 1],
    [0, 1, width, width + 1],
    [0, 1, width, width + 1],
    [0, 1, width, width + 1]
  ]

  const iBlock = [
    [1, width + 1, width * 2 + 1, width * 3 + 1],
    [width, width + 1, width + 2, width + 3],
    [1, width + 1, width * 2 + 1, width * 3 + 1],
    [width, width + 1, width + 2, width + 3]
  ]

  // putting the blocks in a list and setting their initial position/rotation
  const blocks = [lBlock, zBlock, tBlock, oBlock, iBlock]
  let currentPosition = 4
  let currentRotation = 0
  let ghostPosition = 4
  let ghostRotation = 0

  // get a random block
  let random = Math.floor(Math.random() * blocks.length)
  let current = blocks[random][currentRotation]
  let ghostPiece = current


  // draw the different pieces
  // ------------------------------------------------------------------------------------------------
  function draw() {
    current.forEach(index => {
      squares[currentPosition + index].classList.add('block')
      squares[currentPosition + index].style.backgroundColor = colors[random]
    })
  }

  // making an outline
  function drawGhostPiece() {
    // Reset ghostPosition to the initial position
    ghostPosition = currentPosition;

    // Move the ghost outline up to the first available block
    while (!isCollision(ghostPiece, ghostPosition)) {
      ghostPosition += width;
    }

    // Move ghostPosition back down one row to the last valid position
    ghostPosition += width;

    // Draw the ghost outline within the visible grid area
    if (ghostPosition >= 0) {
      ghostPiece.forEach(index => {
        if (ghostPosition + index < squares.length) {
          squares[ghostPosition + index].classList.add('ghost');
        }
      });
    }

    updateCustomColor(random);
    // while (!isCollision(ghostPiece, ghostPosition)) {
    //   ghostPosition += width
    // }

    // let max = 0
    // for (let index = 0; index < ghostPiece.length; index++) {
    //   if (ghostPiece[index] > max) {
    //     max = ghostPiece[index]
    //   }
    // }

    // if (max + ghostPosition < squares.length - width * 2) {
    //   ghostPosition += width
    // }

    // ghostPiece.forEach(index => {
    //   squares[ghostPosition + index].classList.add('ghost')
    // })

    // updateCustomColor(random)
  }

  // undraw the block
  function undraw() {
    current.forEach(index => {
      squares[currentPosition + index].classList.remove('block')
      squares[currentPosition + index].style.backgroundColor = ''
    })
  }

  // undraw the outline
  function undrawGhostPiece() {
    ghostPiece.forEach(index => {
      squares[ghostPosition + index].classList.remove('ghost')
    })
  }

  // make the block move down
  // assign functions to keyCodes
  // ------------------------------------------------------------------------------------------------
  function control(e) {
    if (e.keyCode == 37) {
      moveLeft()
      moveLeftGhost()
    } else if (e.keyCode == 39) {
      moveRight()
      moveRightGhost()
    } else if (e.keyCode == 38) {
      rotate()
      rotateGhostPiece()
    } else if (e.keyCode == 40) {
      moveDown()
    } else if (e.keyCode == 32) {
      while (!isCollision(current, currentPosition)) {
        moveDown();
      }
      moveDown()
      undrawGhostPiece()
    }
  }
  document.addEventListener('keyup', control)
  let escapePressed = false; // Flag to track if the escape key was pressed

  // Event listener to handle the escape key press
  document.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') { // Check if the Esc key was pressed
      if (timerID) {
        clearInterval(timerID);
        timerID = null;
        isPaused = true; // Set the paused state to true
        showPauseScreen(); // Show the pause screen
        // Re-add the space key event listener to handle manual piece movement
        document.addEventListener('keyup', spaceKeyListener);
        escapePressed = true; // Set the flag to true since escape was pressed
      } else {
        if (isPaused) { // Only resume if the game is currently paused
          timerID = setInterval(moveDown, 1000);
          isPaused = false; // Set the paused state to false
          hidePauseScreen(); // Hide the pause screen
          // Remove the space key event listener since the game is running again
          document.removeEventListener('keyup', spaceKeyListener);
        }
        escapePressed = false; // Set the flag to false since escape was released
      }
    }
    // } else if (e.key === ' ' && !escapePressed) { // Check if the space key was pressed
    //   while (!isCollision(current, currentPosition)) {
    //     moveDown();
    //   }
    //   moveDown();
    //   undrawGhostPiece();
    // }
  });

  // movement
  // ------------------------------------------------------------------------------------------------
  function moveDown() {
    undraw()
    currentPosition += width
    draw()
    freeze()
  }

  function moveLeft() {
    undraw()

    const isAtLeftEdge = current.some(index => (currentPosition + index) % width == 0)

    if (!isAtLeftEdge) currentPosition -= 1

    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      currentPosition += 1
    }


    draw()
  }

  function moveLeftGhost() {
    undrawGhostPiece();

    const isAtLeftEdge = ghostPiece.some(index => (ghostPosition + index) % width === 0);

    if (!isAtLeftEdge) {
      ghostPosition -= 1;
    }

    if (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      // If collision occurs, move up to the first available block
      while (ghostPiece.some(index => squares[ghostPosition + index + width].classList.contains('taken'))) {
        ghostPosition -= width;
      }
    }

    // If after moving up, there's a collision again, move back down one row
    while (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      ghostPosition += width;
    }

    drawGhostPiece();
  }

  function moveRight() {
    undraw()

    const isAtRightEdge = current.some(index => (currentPosition + index) % width == width - 1)

    if (!isAtRightEdge) {
      currentPosition += 1
    }

    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      currentPosition -= 1
    }

    draw()
  }

  function moveRightGhost() {
    undrawGhostPiece();

    const isAtRightEdge = ghostPiece.some(index => (ghostPosition + index) % width === width - 1);

    if (!isAtRightEdge) {
      ghostPosition += 1;
    }

    if (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      // If collision occurs, move up to the first available block
      while (ghostPiece.some(index => squares[ghostPosition + index + width].classList.contains('taken'))) {
        ghostPosition -= width;
      }
    }

    // If after moving up, there's a collision again, move back down one row
    while (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      ghostPosition += width;
    }

    drawGhostPiece();
  }

  function rotate() {
    undraw()

    currentRotation++
    if (currentRotation == current.length) {
      currentRotation = 0
    }
    current = blocks[random][currentRotation]
    checkRotatedPosition()

    draw()
  }

  function rotateGhostPiece() {
    undrawGhostPiece();

    ghostRotation++;
    if (ghostRotation === ghostPiece.length) {
      ghostRotation = 0;
    }

    const nextGhostPiece = blocks[random][ghostRotation];

    // Check for collisions when rotating and adjust the position upward if necessary
    while (isCollision(nextGhostPiece, ghostPosition)) {
      ghostPosition -= width;
    }

    ghostPiece = nextGhostPiece;
    drawGhostPiece();
  }
  // ------------------------------------------------------------------------------------------------
  // checking if rotations can be made. if not, we are making sure it doesn't wrap around to the other end

  function isAtRight() {
    return current.some(index => (currentPosition + index + 1) % width === 0)
  }

  function isAtLeft() {
    return current.some(index => (currentPosition + index) % width === 0)
  }

  function checkRotatedPosition(P) {
    P = P || currentPosition       //get current position.  Then, check if the piece is near the left side.
    if ((P + 1) % width < 4) {         //add 1 because the position index can be 1 less than where the piece is (with how they are indexed).     
      if (isAtRight()) {            //use actual position to check if it's flipped over to right side
        currentPosition += 1    //if so, add one to wrap it back around
        checkRotatedPosition(P) //check again.  Pass position from start, since long block might need to move more.
      }
    }
    else if (P % width > 5) {
      if (isAtLeft()) {
        currentPosition -= 1
        checkRotatedPosition(P)
      }
    }
  }

  // doing same for the outlined piece
  function isAtRightGhost() {
    return ghostPiece.some(index => (ghostPosition + index + 1) % width === 0)
  }

  function isAtLeftGhost() {
    return ghostPiece.some(index => (ghostPosition + index) % width === 0)
  }

  function checkRotatedPositionGhost(P) {
    P = P || ghostPosition       //get current position.  Then, check if the piece is near the left side.
    if ((P + 1) % width < 4) {         //add 1 because the position index can be 1 less than where the piece is (with how they are indexed).     
      if (isAtRightGhost()) {            //use actual position to check if it's flipped over to right side
        ghostPosition += 1    //if so, add one to wrap it back around
        checkRotatedPosition(P) //check again.  Pass position from start, since long block might need to move more.
      }
    }
    else if (P % width > 5) {
      if (isAtLeftGhost()) {
        ghostPosition -= 1
        checkRotatedPosition(P)
      }
    }
  }

  // ------------------------------------------------------------------------------------------------
  // helper functions

  function isCollision(type, position) {
    return type.some((index) =>
      squares[position + index + width * 2].classList.contains('taken')
    );
  }

  function freeze() {
    if (current.some(index => squares[currentPosition + index + width].classList.contains('taken'))) {
      current.forEach(index => squares[currentPosition + index].classList.add('taken'))
      undrawGhostPiece()
      random = nextRandom
      nextRandom = Math.floor(Math.random() * blocks.length)
      current = blocks[random][currentRotation]
      ghostPiece = current
      currentPosition = 4
      ghostPosition = 4
      draw()
      displayShape()
      addScore()
      gameOver()
    }
  }


  var root = document.documentElement;

  function updateCustomColor(random) {
    // Update the CSS variable value
    root.style.setProperty('--custom-color', colors[random]);
  }

  // ------------------------------------------------------------------------------------------------
  // show the next block in rotation
  const displaySquares = document.querySelectorAll('.mini-grid div')
  const displayWidth = 4
  const displayIndex = 0

  // the blocks' first rotations
  const upNextBlocks = [
    [1, displayWidth + 1, displayWidth * 2 + 1, 2],
    [0, displayWidth, displayWidth + 1, displayWidth * 2 + 1],
    [1, displayWidth, displayWidth + 1, displayWidth + 2],
    [0, 1, displayWidth, displayWidth + 1],
    [1, displayWidth + 1, displayWidth * 2 + 1, displayWidth * 3 + 1]
  ]

  function displayShape() {
    displaySquares.forEach(square => {
      square.classList.remove('block')
      square.style.backgroundColor = ''
    })
    upNextBlocks[nextRandom].forEach(index => {
      displaySquares[displayIndex + index].classList.add('block')
      displaySquares[displayIndex + index].style.backgroundColor = colors[nextRandom]
    })
  }


  // making start button work
  startButton.addEventListener('click', () => {
    if (timerID) {
      clearInterval(timerID)
      timerID = null
      startButton.disabled = false

    } else {
      draw()
      drawGhostPiece()
      timerID = setInterval(moveDown, 1000)
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      startButton.disabled = true
    }

    startButton.disabled = false
  })

  function addScore() {
    for (let i = 0; i < 199; i += width) {
      const row = [i, i + 1, i + 2, i + 3, i + 4, i + 5, i + 6, i + 7, i + 8, i + 9]

      if (row.every(index => squares[index].classList.contains('taken'))) {
        score += 10
        scoreDisplay.innerHTML = score
        row.forEach(index => {
          squares[index].classList.remove('taken')
          squares[index].classList.remove('block')
          squares[index].classList.remove('ghost')
          squares[index].style.backgroundColor = ''
        })
        const squaresRemoved = squares.splice(i, width)
        squares = squaresRemoved.concat(squares)
        squares.forEach(cell => grid.appendChild(cell))
      }
    }
  }

  // defining when the game is over
  function gameOver() {
    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      scoreDisplay.innerHTML = 'end'
      clearInterval(timerID)
    }
  }

  function showPauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen');
    pauseScreen.style.display = 'block';
  }

  // Function to hide the pause screen
  function hidePauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen');
    pauseScreen.style.display = 'none';
  }


})