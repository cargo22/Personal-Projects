// SearchBar.jsx — the question input and Ask button
// single responsibility: capturing user input and triggering a search

function SearchBar({ question, onQuestionChange, onAsk, onKeyDown, loading, placeholder }) {
  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder={placeholder}
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        onKeyDown={onKeyDown}
      />
      <button onClick={onAsk} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </button>
    </div>
  )
}

export default SearchBar
