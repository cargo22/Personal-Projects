// App.jsx — the entire UI, handles input, API calls, and displaying results

// useState gives the component memory — without it, variables reset on every render
import { useState } from 'react'

// axios handles sending HTTP requests to the backend
import axios from 'axios'

// loads the styles for this component
import './App.css'

function App() {
  // tracks what the user has typed in the input box
  const [question, setQuestion] = useState('')

  // stores the results returned from the backend — null means nothing fetched yet
  const [results, setResults] = useState(null)

  // true while waiting for the backend to respond — controls the "Thinking..." button state
  const [loading, setLoading] = useState(false)

  // stores an error message if something goes wrong
  const [error, setError] = useState(null)

  async function handleAsk() {
    // do nothing if the input is empty or just whitespace
    if (!question.trim()) return

    // reset state before sending a new request
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      // send the question to the FastAPI backend and wait for the response
      // this goes to api_server.py
      const response = await axios.post('http://localhost:8000/ask', { question })

      // store the results array so it renders in the table below
      setResults(response.data.results)
    } catch {
      setError('Something went wrong. Is the backend running?')
    } finally {
      // always turn off loading when done, whether it succeeded or failed
      setLoading(false)
    }
  }

  // lets the user press Enter instead of clicking the Ask button
  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      handleAsk()
    }
  }

  // extracts column names from the first result row to use as table headers
  // e.g. {"name": "LeBron", "points": 30} → ["name", "points"]
  let columns = []
  if (results && results.length > 0) {
    columns = Object.keys(results[0])
  }

  return (
    <div className="container">
      <h1>Sports Oracle</h1>
      <p className="subtitle">Ask anything about NBA history</p>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Who scored the most points in a single game in 2023-24?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}  // updates question state on every keystroke
          onKeyDown={handleKeyDown}
        />
        {/* button is disabled while loading to prevent duplicate requests */}
        <button onClick={handleAsk} disabled={loading}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {/* only renders if there's an error */}
      {error && <p className="error">{error}</p>}

      {/* only renders if results came back empty */}
      {results && results.length === 0 && (
        <p className="no-results">No results found.</p>
      )}

      {/* only renders if we have results — builds the table dynamically from the data */}
      {results && results.length > 0 && (
        <table>
          <thead>
            <tr>
              {/* map over column names to create headers */}
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* map over each result row */}
            {results.map((row, i) => (
              <tr key={i}>
                {/* map over columns to fill in each cell — ?? '—' shows a dash if value is missing */}
                {columns.map((col) => (
                  <td key={col}>{row[col] ?? '—'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

// default export so main.jsx can import this as App
export default App
