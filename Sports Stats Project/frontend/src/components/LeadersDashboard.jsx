import { useState, useEffect } from "react"
import "../styles/LeadersDashboard.css"

const BASE_URL = "http://localhost:8000"

const STAT_LABELS = { ppg: "Points", rpg: "Rebounds", apg: "Assists" }

function LeadersTable({ stat, rows }) {
  const label = stat.toUpperCase()
  return (
    <div className="leaders-card">
      <h3>{STAT_LABELS[stat]} Leaders</h3>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Player</th>
            <th>{label}</th>
            <th>GP</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((player, i) => (
            <tr key={i}>
              <td className="rank">{i + 1}</td>
              <td>{player.name}</td>
              <td className="stat-value">{player.value}</td>
              <td className="gp">{player.gp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function LeadersDashboard() {
  const [leaders, setLeaders] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState("regular")

  useEffect(() => {
    fetch(`${BASE_URL}/api/leaders`)
      .then(r => r.json())
      .then(data => { setLeaders(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <p className="leaders-loading">Loading leaders...</p>
  if (!leaders) return null

  const section = leaders[tab]

  return (
    <div className="leaders-dashboard">
      <p className="leaders-season">2025-26 Season Leaders</p>
      <div className="leaders-tabs">
        <button
          className={tab === "regular" ? "active" : ""}
          onClick={() => setTab("regular")}
        >
          Regular Season
        </button>
        <button
          className={tab === "playoffs" ? "active" : ""}
          onClick={() => setTab("playoffs")}
        >
          Playoffs
        </button>
      </div>
      <div className="leaders-grid">
        {Object.keys(STAT_LABELS).map(stat => (
          <LeadersTable key={stat} stat={stat} rows={section[stat]} />
        ))}
      </div>
    </div>
  )
}
