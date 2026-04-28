// ResultsTable.jsx — displays the query results as a table
// single responsibility: rendering whatever data the backend returns

function ResultsTable({ results }) {
  if (!results || results.length === 0) return null

  const columns = Object.keys(results[0])

  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {results.map((row, i) => (
          <tr key={i}>
            {columns.map((col) => (
              <td key={col}>{row[col] ?? "—"}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default ResultsTable
