// useTheme.js — applies the correct CSS theme class to the page when mode changes
// single responsibility: syncing the mode state to the HTML class list

import { useEffect } from "react"

export function useTheme(mode) {
  useEffect(() => {
    document.documentElement.classList.remove("present", "future")
    if (mode === "present") {
      document.documentElement.classList.add("present")
    } else if (mode === "future") {
      document.documentElement.classList.add("future")
    }
  }, [mode])
}
