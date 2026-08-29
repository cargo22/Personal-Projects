// LeadersDashboard.jsx — displays current season leaders for players and teams
// single responsibility: stats hub for the 'present' toggle

import { useState, useEffect } from "react"
import "../styles/LeadersDashboard.css"

const BASE_URL = "http://localhost:8000"

const PLAYER_SORT_OPTIONS = [
  { key: "ppg", label: "PTS" },
  { key: "rpg", label: "REB" },
  { key: "apg", label: "AST" },
]

const TEAM_VIEW_OPTIONS = [
  { key: "record", label: "Record" },
  { key: "ppg",   label: "PPG" },
  { key: "ortg",  label: "ORtg" },
  { key: "drtg",  label: "DRtg" },
  { key: "pace",  label: "Pace" },
]

function PlayerTable({ players }) {
  const [sortBy, setSortBy] = useState("ppg")

  const sorted = [...players].sort((a, b) => b[sortBy] - a[sortBy])

  return (
    <div className="leaders-card">
      <div className="card-header">
        <h3>Player Leaders</h3>
        <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
          {PLAYER_SORT_OPTIONS.map(o => (
            <option key={o.key} value={o.key}>{o.label}</option>
          ))}
        </select>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Player</th>
            <th className={sortBy === "ppg" ? "col-active" : ""}>PTS</th>
            <th className={sortBy === "rpg" ? "col-active" : ""}>REB</th>
            <th className={sortBy === "apg" ? "col-active" : ""}>AST</th>
            <th>GP</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((p, i) => (
            <tr key={p.name}>
              <td className="rank">{i + 1}</td>
              <td>{p.name}</td>
              <td className={sortBy === "ppg" ? "stat-value" : ""}>{p.ppg}</td>
              <td className={sortBy === "rpg" ? "stat-value" : ""}>{p.rpg}</td>
              <td className={sortBy === "apg" ? "stat-value" : ""}>{p.apg}</td>
              <td className="gp">{p.gp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function TeamTable({ teamsRecord, teamsStats }) {
  const [view, setView] = useState("record")

  const isRecord = view === "record"

  const data = isRecord
    ? teamsRecord
    : [...teamsStats].sort((a, b) =>
        view === "drtg" ? a[view] - b[view] : b[view] - a[view]
      )

  const viewLabel = TEAM_VIEW_OPTIONS.find(o => o.key === view)?.label

  return (
    <div className="leaders-card">
      <div className="card-header">
        <h3>Team Leaders</h3>
        <select value={view} onChange={e => setView(e.target.value)}>
          {TEAM_VIEW_OPTIONS.map(o => (
            <option key={o.key} value={o.key}>{o.label}</option>
          ))}
        </select>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Team</th>
            {isRecord ? (
              <>
                <th className="col-active">W</th>
                <th>L</th>
                <th>Win%</th>
              </>
            ) : (
              <>
                <th className="col-active">{viewLabel}</th>
                <th>GP</th>
              </>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((t, i) => (
            <tr key={t.name}>
              <td className="rank">{i + 1}</td>
              <td>{t.name}</td>
              {isRecord ? (
                <>
                  <td className="stat-value">{t.wins}</td>
                  <td>{t.losses}</td>
                  <td className="gp">{t.win_pct?.toFixed(3)}</td>
                </>
              ) : (
                <>
                  <td className="stat-value">{t[view]}</td>
                  <td className="gp">{t.gp}</td>
                </>
              )}
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
        <PlayerTable players={section.players} />
        <TeamTable teamsRecord={section.teams_record} teamsStats={section.teams_stats} />
      </div>
    </div>
  )
}
