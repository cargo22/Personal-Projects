// useTypingPlaceholder.js — handles rotating and typing the placeholder text
// single responsibility: all placeholder animation logic lives here

import { useState, useEffect } from "react"
import { pastPlaceholders, presentPlaceholders, futurePlaceholders } from "../constants/placeholders"

// this function just retrieves the list of placeholder questions depending on the mode we are on
function getList(mode) {
  if (mode === "present") {
    return presentPlaceholders
  }  
  if (mode === "future") {
    return futurePlaceholders
  }
  return pastPlaceholders
}

// function that adds the typing effect
export function useTypingPlaceholder(mode) {
  // defining variables that show what index the question is on and which question specifically
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [displayedPlaceholder, setDisplayedPlaceholder] = useState("")

  // rotate to the next placeholder every 7 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((current) => {
        const list = getList(mode)
        // updates the sentence currently displaying
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
    // adding the typing effect
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
