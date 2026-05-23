// oracle.js — handles all API calls to the backend
// single responsibility: sending questions and receiving results

import axios from "axios"

const BASE_URL = "http://localhost:8000"

// sends question to backend and returns {summary, results} via api_server.py and ai_query.py
export async function askOracle(question, mode = "past") {
  const response = await axios.post(`${BASE_URL}/ask`, { question, mode })
  return {
    summary: response.data.summary,
    results: response.data.results,
  }
}
