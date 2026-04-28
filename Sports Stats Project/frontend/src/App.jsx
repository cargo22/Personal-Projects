// App.jsx — the main component, orchestrates all state and renders the layout
// single responsibility: wiring together the smaller components and hooks

import { useState } from "react"
import "./App.css"

import Toggle from "./components/Toggle"
import SearchBar from "./components/SearchBar"
import ResultsTable from "./components/ResultsTable"

import { useTheme } from "./hooks/useTheme"
import { useTypingPlaceholder } from "./hooks/useTypingPlaceholder"
import { askOracle } from "./api/oracle"

function App() {
  const [mode, setMode] = useState("past")
  const [question, setQuestion] = useState("")
  const [summary, setSummary] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // applies the correct CSS theme class when mode changes
  useTheme(mode)

  // returns the currently typed-out placeholder string
  const placeholder = useTypingPlaceholder(mode)

  async function handleAsk() {
    if (!question.trim()) return

    setLoading(true)
    setError(null)
    setSummary(null)
    setResults(null)

    try {
      const data = await askOracle(question)
      setSummary(data.summary)
      setResults(data.results)
    } catch {
      setError("Something went wrong. Is the backend running?")
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleAsk()
  }

  const subtitle =
    mode === "past" ? "Ask anything about NBA history" :
    mode === "present" ? "Ask anything about the current season" :
    "Ask for predictions and forecasts"

  return (
    <div className="container">
      <div className="hero">
        <Toggle mode={mode} onModeChange={setMode} />
        <h1>Sports Oracle</h1>
        <p className="subtitle">{subtitle}</p>
        <SearchBar
          question={question}
          onQuestionChange={setQuestion}
          onAsk={handleAsk}
          onKeyDown={handleKeyDown}
          loading={loading}
          placeholder={placeholder}
        />
      </div>

      {error && <p className="error">{error}</p>}
      {results && results.length === 0 && <p className="no-results">No results found.</p>}
      {summary && <p className="summary">{summary}</p>}
      <ResultsTable results={results} />
    </div>
  )
}

export default App
