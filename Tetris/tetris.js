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

  // making an outline piece that shows where the piece will end up
  function drawGhostPiece() {
    ghostPosition = currentPosition

    // making sure the outlined piece moves up if piece is already there
    while (!isCollision(ghostPiece, ghostPosition)) {
      ghostPosition += width
    }

    // move ghostPosition back down one row to the last valid position
    ghostPosition += width

    // draw the ghost outline within the visible grid area
    if (ghostPosition >= 0) {
      ghostPiece.forEach(index => {
        if (ghostPosition + index < squares.length) {
          squares[ghostPosition + index].classList.add('ghost')
        }
      });
    }

    updateCustomColor(random)
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
    // left arrow
    if (e.keyCode == 37) {
      moveLeft()
      moveLeftGhost()
      // right arrow
    } else if (e.keyCode == 39) {
      moveRight()
      moveRightGhost()
      // up arrow  
    } else if (e.keyCode == 38) {
      rotate()
      rotateGhostPiece()
      // down arrow  
    } else if (e.keyCode == 40) {
      moveDown()
      // space bar
    } else if (e.keyCode == 32) {
      while (!isCollision(current, currentPosition)) {
        moveDown()
      }
      moveDown()
      undrawGhostPiece()
    }
  }

  document.addEventListener('keyup', control)

  // programming a pause screen
  // ------------------------------------------------------------------------------------------------
  let escapePressed = false

  document.addEventListener('keyup', (e) => {
    if (e.key === 'Escape') {
      // checking if the pause screen is already there
      if (timerID) {
        clearInterval(timerID)
        timerID = null
        isPaused = true
        showPauseScreen()
        audio.pause()
        escapePressed = true
      } else {
        if (isPaused) {
          timerID = setInterval(moveDown, 1000)
          isPaused = false
          hidePauseScreen()
          audio.play()
        }
        escapePressed = false
      }
    }
  });

  //programming a reset button
  // ------------------------------------------------------------------------------------------------

  function resetGame() {
    // removing all blocks from the grid
    squares.slice(0, 200).forEach(square => {
      square.classList.remove('taken')
      square.classList.remove('block')
      square.classList.remove('ghost')
      square.style.backgroundColor = ''
    });

    startButton.disabled = false
    audio.currentTime = 0
    audio.play()

    if (timerID) {
      clearInterval(timerID)
      timerID = null
      isPaused = false
      hidePauseScreen()
      scoreDisplay.innerHTML = score
    } else {
      // resetting all values
      currentPosition = 4
      currentRotation = 0
      ghostPosition = 4
      ghostRotation = 0
      random = Math.floor(Math.random() * blocks.length)
      current = blocks[random][currentRotation]
      ghostPiece = current
      score = 0
      scoreDisplay.innerHTML = score
      draw()
      drawGhostPiece()
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      hidePauseScreen()

      // start game again
      timerID = setInterval(moveDown, 1000);
    }

  }

  const resetButton = document.getElementById('restartButton')
  const resumeButton = document.getElementById('resumeButton')
  resetButton.addEventListener('click', resetGame)
  resumeButton.addEventListener('click', () => {
    hidePauseScreen()
    draw()
    drawGhostPiece()
    timerID = setInterval(moveDown, 1000)
    nextRandom = Math.floor(Math.random() * blocks.length)
    displayShape()
    audio.play()
    startButton.disabled = false
  })

  // movement
  // ------------------------------------------------------------------------------------------------
  let isLocked = false
  const lockDelay = 1000

  function moveDown() {
    undraw();
    currentPosition += width;

    // Check if the block has reached the last layer
    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      // Block has reached the last layer
      if (!isLocked) {
        // If not locked, initiate the lock delay
        isLocked = true;
        setTimeout(() => {
          isLocked = false;
        }, lockDelay);
      } else {
        // If locked, proceed with usual behavior (lock the block)
        freeze();
      }

      draw()
    }
  }

  function moveLeft() {
    undraw()

    if (!isLocked) {
      const isAtLeftEdge = current.some(index => (currentPosition + index) % width === 0);
      if (!isAtLeftEdge) {
        currentPosition -= 1;
      }
      if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
        currentPosition += 1;
      }
    }

    draw()
  }

  function moveLeftGhost() {
    undrawGhostPiece()

    const isAtLeftEdge = ghostPiece.some(index => (ghostPosition + index) % width === 0)

    if (!isAtLeftEdge) {
      ghostPosition -= 1
    }

    if (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      while (ghostPiece.some(index => squares[ghostPosition + index + width].classList.contains('taken'))) {
        // moving piece up until the first available square
        ghostPosition -= width
      }
    }


    while (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      ghostPosition += width
    }

    drawGhostPiece()
  }

  function moveRight() {
    undraw()

    const isAtRightEdge = current.some(index => (currentPosition + index) % width == width - 1)

    if (!isLocked) {
      const isAtRightEdge = current.some(index => (currentPosition + index) % width === width - 1);
      if (!isAtRightEdge) {
        currentPosition += 1;
      }
      if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
        currentPosition -= 1;
      }
    }


    draw()
  }

  function moveRightGhost() {
    undrawGhostPiece()

    const isAtRightEdge = ghostPiece.some(index => (ghostPosition + index) % width === width - 1)

    if (!isAtRightEdge) {
      ghostPosition += 1
    }

    if (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      while (ghostPiece.some(index => squares[ghostPosition + index + width].classList.contains('taken'))) {
        // moving piece up until the first available square
        ghostPosition -= width
      }
    }

    while (ghostPiece.some(index => squares[ghostPosition + index].classList.contains('taken'))) {
      ghostPosition += width
    }

    drawGhostPiece()
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
    undrawGhostPiece()

    ghostRotation++
    if (ghostRotation === ghostPiece.length) {
      ghostRotation = 0
    }

    const nextGhostPiece = blocks[random][ghostRotation]

    // checking for collisions when rotating and adjust the position upward if necessary
    while (isCollision(nextGhostPiece, ghostPosition)) {
      ghostPosition -= width
    }

    ghostPiece = nextGhostPiece
    drawGhostPiece()
  }

  // checking if rotations can be made. if not, we are making sure it doesn't wrap around to the other end
  // ------------------------------------------------------------------------------------------------

  function isAtRight() {
    return current.some(index => (currentPosition + index + 1) % width === 0)
  }

  function isAtLeft() {
    return current.some(index => (currentPosition + index) % width === 0)
  }

  // checking to see if the rotation can be made within the grid's width. if not, rotate in a way where the block
  // does not wrap around the grid
  function checkRotatedPosition(P) {
    P = P || currentPosition
    if ((P + 1) % width < 4) {
      if (isAtRight()) {
        currentPosition += 1
        checkRotatedPosition(P)
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
    P = P || ghostPosition
    if ((P + 1) % width < 4) {
      if (isAtRightGhost()) {
        ghostPosition += 1
        checkRotatedPosition(P)
      }
    }
    else if (P % width > 5) {
      if (isAtLeftGhost()) {
        ghostPosition -= 1
        checkRotatedPosition(P)
      }
    }
  }

  // helper functions
  // ------------------------------------------------------------------------------------------------

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


  var root = document.documentElement

  function updateCustomColor(random) {
    // update the CSS variable value to be the same as the block color
    root.style.setProperty('--custom-color', colors[random])
  }

  // functions for the pause screen
  function showPauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen')
    pauseScreen.style.display = 'block'
  }

  function hidePauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen')
    pauseScreen.style.display = 'none'
  }

  // show the next block in rotation
  // ------------------------------------------------------------------------------------------------

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

  const audio = document.getElementById('backgroundMusic')
  let isMusicPlaying = false

  // making start button work
  startButton.addEventListener('click', () => {
    if (timerID) {
      clearInterval(timerID)
      timerID = null
      startButton.disabled = false
      audio.pause()
      showPauseScreen()
      resumePressed = false
    } else {
      draw()
      drawGhostPiece()
      timerID = setInterval(moveDown, 1000)
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      startButton.disabled = true
      audio.play()
      startButton.innerText = 'Pause'
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



})