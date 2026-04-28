// Toggle.jsx — the Past / Present / Future mode switcher
// single responsibility: rendering the toggle buttons and signaling mode changes

function Toggle({ mode, onModeChange }) {
  function getClass(buttonMode) {
    return mode === buttonMode ? "active" : ""
  }

  return (
    <div className="toggle">
      <button className={getClass("past")} onClick={() => onModeChange("past")}>Past</button>
      <button className={getClass("present")} onClick={() => onModeChange("present")}>Present</button>
      <button className={getClass("future")} onClick={() => onModeChange("future")}>Future</button>
    </div>
  )
}

export default Toggle
