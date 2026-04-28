// useTypingPlaceholder.js — handles rotating and typing the placeholder text
// single responsibility: all placeholder animation logic lives here

import { useState, useEffect } from "react"
import { pastPlaceholders, presentPlaceholders, futurePlaceholders } from "../constants/placeholders"

function getList(mode) {
  if (mode === "present") return presentPlaceholders
  if (mode === "future") return futurePlaceholders
  return pastPlaceholders
}

export function useTypingPlaceholder(mode) {
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [displayedPlaceholder, setDisplayedPlaceholder] = useState("")

  // rotate to the next placeholder every 7 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((current) => {
        const list = getList(mode)
        return current === list.length - 1 ? 0 : current + 1
      })
    }, 7000)
    return () => clearInterval(interval)
  }, [mode])

  // type out the current placeholder one character at a time
  useEffect(() => {
    const currentPlaceholder = getList(mode)[placeholderIndex]
    setDisplayedPlaceholder("")

    let i = 0
    const typing = setInterval(() => {
      if (i < currentPlaceholder.length) {
        setDisplayedPlaceholder(currentPlaceholder.slice(0, i + 1))
        i++
      } else {
        clearInterval(typing)
      }
    }, 40)

    return () => clearInterval(typing)
  }, [placeholderIndex, mode])

  return displayedPlaceholder
}
