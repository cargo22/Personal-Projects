document.addEventListener('DOMContentLoaded', () => {
  // necessary variables 
  // ------------------------------------------------------------------------------------------------
  const grid = document.querySelector('.grid')
  let squares = Array.from(document.querySelectorAll('.grid div'))
  const scoreDisplay = document.querySelector('#score')
  const levelDisplay = document.querySelector('#level')
  const startButton = document.querySelector('#startButton')
  let nextRandom = 0
  const width = 10
  let timerID
  let score = 0
  let fallSpeed = 1000
  const colors = [
    'orange',
    'red',
    'purple',
    'green',
    'blue',
    'yellow',
    'cyan'
  ]

  // drawing the blocks. each different list is a rotated form of the original block
  // ------------------------------------------------------------------------------------------------
  const lBlock = [
    [1, width + 1, width * 2 + 1, 2],
    [width, width + 1, width + 2, width * 2 + 2],
    [1, width + 1, width * 2 + 1, width * 2],
    [width, width * 2, width * 2 + 1, width * 2 + 2]
  ]

  const jBlock = [
    [1, 2, width + 2, width * 2 + 2],
    [width + 2, width * 2, width * 2 + 1, width * 2 + 2],
    [1, width + 1, width * 2 + 1, width * 2 + 2],
    [width, width + 1, width + 2, width * 2]
  ]

  const zBlock = [
    [0, width, width + 1, width * 2 + 1],
    [width + 1, width + 2, width * 2, width * 2 + 1],
    [0, width, width + 1, width * 2 + 1],
    [width + 1, width + 2, width * 2, width * 2 + 1]
  ]

  const sBlock = [
    [1, width, width + 1, width * 2],
    [0, 1, width + 1, width + 2],
    [1, width, width + 1, width * 2],
    [0, 1, width + 1, width + 2]
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
  const blocks = [lBlock, zBlock, tBlock, oBlock, iBlock, jBlock, sBlock]
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

  // undraw (erase) the block
  function undraw() {
    current.forEach(index => {
      squares[currentPosition + index].classList.remove('block')
      squares[currentPosition + index].style.backgroundColor = ''
    })
  }

  // undraw the outlined piece
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
        moveDownSpace()
      }
      moveDownSpace()
    }
  }

  document.addEventListener('keyup', control)

  // programming a pause screen
  // ------------------------------------------------------------------------------------------------
  let escapePressed = false

  document.addEventListener('keyup', (e) => {
    if (e.key == 'Escape') {
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
          timerID = setInterval(moveDown, fallSpeed)
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

  // function that starts a brand new game from scratch
  function resetGame() {
    // removing all blocks from the grid
    squares.slice(0, 200).forEach(square => {
      square.classList.remove('taken')
      square.classList.remove('block')
      square.classList.remove('ghost')
      square.style.backgroundColor = ''
    });

    // making sure audio restarts
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
      // resetting all values to start fresh
      currentPosition = 4
      currentRotation = 0
      ghostPosition = 4
      ghostRotation = 0
      random = Math.floor(Math.random() * blocks.length)
      current = blocks[random][currentRotation]
      ghostPiece = current
      score = 0
      fallSpeed = 1000
      currentLevel = 0
      scoreDisplay.innerHTML = score
      levelDisplay.innerHTML = currentLevel
      draw()
      drawGhostPiece()
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      hidePauseScreen()

      // start game again
      timerID = setInterval(moveDown, fallSpeed)
    }

  }

  // this function is the same as the one above, but this one is specifically for the restart button that is pressed when the 
  // game is over
  function resetGameFinal() {
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
      hideFinalScreen()
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
      fallSpeed = 1000
      currentLevel = 0
      scoreDisplay.innerHTML = score
      levelDisplay.innerHTML = currentLevel
      draw()
      drawGhostPiece()
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      hideFinalScreen()

      // start game again
      timerID = setInterval(moveDown, fallSpeed)
    }

  }

  // applying the functions when the buttons are pressed
  // ------------------------------------------------------------------------------------------------
  const resetButton = document.getElementById('restartButton')
  const resumeButton = document.getElementById('resumeButton')

  // giving function to the restart and resume buttons
  resetButton.addEventListener('click', resetGame)
  resumeButton.addEventListener('click', () => {
    hidePauseScreen()
    draw()
    drawGhostPiece()
    timerID = setInterval(moveDown, fallSpeed)
    audio.play()
    startButton.disabled = false
  })

  // programming button on game over screen
  const finalRestartButton = document.getElementById('freshRestart')
  finalRestartButton.addEventListener('click', resetGameFinal)

  // movement
  // ------------------------------------------------------------------------------------------------

  // this function moves the block down one row
  function moveDown() {
    if (lockingDelay) {
      return
    }

    undraw()
    currentPosition += width
    draw()
    freeze()
    gameOver()
  }

  // this function is the same as the one above, it just doesn't have a locking delay. this function
  // is specifically meant for when the space bar is pressed
  function moveDownSpace() {
    undraw()
    undrawGhostPiece()
    currentPosition += width
    draw()
    drawGhostPiece()
    freezeSpace()
  }

  // this function moves the block one tile to the left
  function moveLeft() {
    undraw()

    const isAtLeftEdge = current.some(index => (currentPosition + index) % width === 0)

    // making sure the block can't move out of range
    if (!isAtLeftEdge) {
      currentPosition -= 1
    }

    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      currentPosition += 1
    }


    draw()
  }

  // this function moves the outlined piece one to the left when the normal piece moves left
  // as well
  function moveLeftGhost() {
    undrawGhostPiece()

    const isAtLeftEdge = ghostPiece.some(index => (ghostPosition + index) % width === 0)

    // making sure the block can't move out of range
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

  // this function moves the block one tile to the right
  function moveRight() {
    undraw()

    const isAtRightEdge = current.some(index => (currentPosition + index) % width === width - 1)

    // making sure the block doesn't move out of range
    if (!isAtRightEdge) {
      currentPosition += 1
    }

    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      currentPosition -= 1
    }

    draw()
  }

  // same as the one above, but for the outlined piece
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

  // this function rotates the piece to the next available list the block presents
  function rotate() {
    undraw()

    // keeping current rotation
    let prevRotation = currentRotation
    currentRotation++

    // wrapping around the lists, so there's no out of bounds error
    if (currentRotation == current.length) {
      currentRotation = 0
    }

    const newCurrent = blocks[random][currentRotation]

    // making sure rotate isn't possible if a collision is happening
    if (!isCollision(current, currentPosition)) {
      current = newCurrent
    } else {
      currentRotation = prevRotation
    }
    checkRotatedPosition()

    draw()
  }

  // same as above, but this one rotates the outlined piece
  function rotateGhostPiece() {
    undrawGhostPiece()
    let prevPiece = ghostPiece

    ghostRotation++
    if (ghostRotation === ghostPiece.length) {
      ghostRotation = 0
    }

    while (isCollision(ghostPiece, ghostPosition)) {
      // checking for collisions when rotating and adjust the position upward if necessary
      ghostPosition -= width
    }

    const newGhostPiece = blocks[random][ghostRotation]

    // if there's a collision with the actual block, the outlined piece won't change either
    if (!isCollision(current, currentPosition)) {
      ghostPiece = newGhostPiece
    } else {
      ghostPiece = prevPiece
    }
    checkRotatedPositionGhost()
    drawGhostPiece()
  }

  // checking if rotations can be made. if not, we are making sure it doesn't wrap around to the other end
  // ------------------------------------------------------------------------------------------------

  // checking to see if the block is at the right edge of the grid
  function isAtRight() {
    return current.some(index => (currentPosition + index + 1) % width === 0)
  }

  // checking to see if the block is at the left edge of the grid
  function isAtLeft() {
    return current.some(index => (currentPosition + index) % width === 0)
  }

  // doing same for the outlined piece
  function isAtRightGhost() {
    return ghostPiece.some(index => (ghostPosition + index + 1) % width === 0)
  }

  function isAtLeftGhost() {
    return ghostPiece.some(index => (ghostPosition + index) % width === 0)
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

  // checking to see if there is a collision with an already established block.
  function isCollision(type, position) {
    return type.some((index) => {
      const nextIndex = position + index + width * 2
      const isValidIndex = nextIndex >= 0 && nextIndex < squares.length

      if (isValidIndex) {
        return squares[nextIndex].classList.contains('taken')
      }

      return true
    });
  }

  let lockingDelay = false

  // function that is called when a block reaches the last available position
  function freeze() {
    // checking if block is in contact with a 'taken' block
    if (current.some(index => squares[currentPosition + index + width].classList.contains('taken'))) {
      const isAtBottom = current.some(index => (currentPosition + index) + width * 2 >= 200)

      // setting a delay so that user can move left and right before piece locks in place
      if (isAtBottom || current.some(index => squares[currentPosition + index + width].classList.contains('taken'))) {
        lockingDelay = true

        // setting delay to 300ms
        const delayLock = setTimeout(() => {
          clearTimeout(delayLock)
          lockingDelay = false
          lockPiece()
        }, 300)

        document.addEventListener('keydown', (e) => {
          if (lockingDelay) {
            e.preventDefault()
          }

          if (e.key === 'ArrowLeft') {
            moveLeft()
          } else if (e.key === 'ArrowRight') {
            moveRight()
          }

        }, { once: true })
      } else {
        lockPiece()
      }
    }
  }

  // freeze function meant for when the space bar is pressed. no delay
  function freezeSpace() {
    if (current.some(index => squares[currentPosition + index + width].classList.contains('taken'))) {
      current.forEach(index => squares[currentPosition + index].classList.add('taken'))
      undrawGhostPiece()
      currentRotation = 0
      ghostRotation = 0
      random = nextRandom
      nextRandom = Math.floor(Math.random() * blocks.length)
      current = blocks[random][currentRotation]
      ghostPiece = current
      currentPosition = 4
      ghostPosition = 4
      drawGhostPiece()
      draw()
      addScore()
      displayShape()
    }
    while (!isCollision(ghostPiece, ghostPosition)) {
      ghostPosition += width
    }
    ghostPosition -= width
    drawGhostPiece()
  }

  // the function that locks the block in place
  function lockPiece() {
    current.forEach(index => squares[currentPosition + index].classList.add('taken'))
    undrawGhostPiece()
    currentRotation = 0
    ghostRotation = 0
    random = nextRandom
    nextRandom = Math.floor(Math.random() * blocks.length)
    current = blocks[random][currentRotation]
    ghostPiece = current
    currentPosition = 4
    ghostPosition = 4
    drawGhostPiece()
    draw()
    displayShape()
    addScore()
  }

  var root = document.documentElement

  // this changes the colors of the blocks
  function updateCustomColor(random) {
    // update the CSS variable value to be the same as the block color
    root.style.setProperty('--custom-color', colors[random])
  }

  // functions for the different screen scenarios
  // ------------------------------------------------------------------------------------------------

  function showPauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen')
    pauseScreen.style.display = 'block'
  }

  function hidePauseScreen() {
    const pauseScreen = document.getElementById('pauseScreen')
    pauseScreen.style.display = 'none'
  }

  function showFinalScreen() {
    const finalScreen = document.getElementById('resultScreen')
    finalScreen.style.display = 'block'
  }

  function hideFinalScreen() {
    const finalScreen = document.getElementById('resultScreen')
    finalScreen.style.display = 'none'
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
    [1, displayWidth + 1, displayWidth * 2 + 1, displayWidth * 3 + 1],
    [1, 2, displayWidth + 2, displayWidth * 2 + 2],
    [1, displayWidth, displayWidth + 1, displayWidth * 2]
  ]

  // function to display the upcoming shape in the mini grid to the side
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
  const volumeSlider = document.getElementById('volumeSlider')

  // programming a volume slider
  volumeSlider.addEventListener('input', () => {
    const volumeValue = parseFloat(volumeSlider.value)
    audio.volume = volumeValue
  })

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
      timerID = setInterval(moveDown, fallSpeed)
      nextRandom = Math.floor(Math.random() * blocks.length)
      displayShape()
      startButton.disabled = true
      audio.play()
      startButton.innerText = 'Pause'
    }
    startButton.disabled = false
  })

  // function to make sure the score is calculated correctly
  function addScore() {
    for (let i = 0; i < 199; i += width) {
      const row = [i, i + 1, i + 2, i + 3, i + 4, i + 5, i + 6, i + 7, i + 8, i + 9]

      // checking if every block in the row is 'taken'
      if (row.every(index => squares[index].classList.contains('taken'))) {
        addLevel()
        score += 10
        scoreDisplay.innerHTML = score

        // removes the row
        current.forEach(index => {
          squares[currentPosition + index].classList.remove('block')
          squares[currentPosition + index].style.backgroundColor = ''
        })

        // removes every block and sets it to the original color
        row.forEach(index => {
          squares[index].classList.remove('taken')
          squares[index].classList.remove('block')
          squares[index].classList.remove('ghost')
          squares[index].style.backgroundColor = ''
        })

        // adding deleted row to the top so that we don't lose any rows
        const squaresRemoved = squares.splice(i, width)
        squares = squaresRemoved.concat(squares)
        squares.forEach(cell => grid.appendChild(cell))

        draw()
      }
    }
  }

  // function that determines what happens when the game is over
  function gameOver() {
    if (current.some(index => squares[currentPosition + index].classList.contains('taken'))) {
      clearInterval(timerID)
      timerID = null
      showFinalScreen()
      audio.pause()
    }
  }



  // adding levels to the game
  // ------------------------------------------------------------------------------------------------
  let currentLevel = 0
  levelDisplay.innerHTML = currentLevel

  // function that updates the level depending on the score and also speeds up the falling time
  function addLevel() {
    if (score % 100 == 0) {
      currentLevel++
      fallSpeed = fallSpeed * .85
      clearInterval(timerID)
      timerID = setInterval(moveDown, fallSpeed)
      console.log(fallSpeed)
      levelDisplay.innerHTML = currentLevel
    }
  }

})