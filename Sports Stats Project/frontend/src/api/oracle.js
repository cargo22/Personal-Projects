// oracle.js — handles all API calls to the backend
// single responsibility: sending questions and receiving results

import axios from "axios"

const BASE_URL = "http://localhost:8000"

export async function askOracle(question) {
  const response = await axios.post(`${BASE_URL}/ask`, { question })
  return {
    summary: response.data.summary,
    results: response.data.results,
  }
}
