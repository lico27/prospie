import { useState, useEffect } from "react"
import { fetchRandomPairs, fetchEnrichedPair, submitEvaluation } from "../utils/dataFetcher"
import PairDisplay from "./PairDisplay"
import RatingSlider from "./RatingSlider"

function EvaluationForm() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pairs, setPairs] = useState([])
  const [currentPairIndex, setCurrentPairIndex] = useState(0)
  const [currentPairData, setCurrentPairData] = useState(null)
  const [ratings, setRatings] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)

  useEffect(() => {
    async function initialize() {
      try {
        const randomPairs = await fetchRandomPairs(3)
        const enrichedPair = await fetchEnrichedPair(randomPairs[0])
        setPairs(randomPairs)
        setCurrentPairData(enrichedPair)
        setLoading(false)
      } catch (err) {
        setError(err.message || "Failed to load evaluation pairs")
        setLoading(false)
      }
    }
    initialize()
  }, [])

  useEffect(() => {
    if (pairs.length > 0 && currentPairIndex > 0) {
      loadCurrentPair()
    }
  }, [currentPairIndex])

  async function loadCurrentPair() {
    try {
      setLoading(true)
      const enrichedPair = await fetchEnrichedPair(pairs[currentPairIndex])
      setCurrentPairData(enrichedPair)
      setLoading(false)
    } catch (err) {
      setError(err.message || "Failed to load pair data")
      setLoading(false)
    }
  }

  function handleRatingChange(rating) {
    setRatings(prev => ({
      ...prev,
      [pairs[currentPairIndex].id]: rating
    }))
  }

  function handleNext() {
    if (currentPairIndex < pairs.length - 1) {
      setCurrentPairIndex(currentPairIndex + 1)
    }
  }

  function handlePrevious() {
    if (currentPairIndex > 0) {
      setCurrentPairIndex(currentPairIndex - 1)
    }
  }

  async function handleSubmit() {
    try {
      setSubmitting(true)
      await Promise.all(
        Object.entries(ratings).map(([pairId, rating]) =>
          submitEvaluation(Number(pairId), rating)
        )
      )
      setCompleted(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <p>Loading evaluation pairs...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card error">
        <p>Error: {error}</p>
      </div>
    )
  }

  if (completed) {
    return (
      <div className="card">
        <h2>Submission complete!</h2>
        <p>Thank you so much for submitting your evaluations. Your help is much appreciated.</p>
      </div>
    )
  }

  if (!currentPairData) {
    return (
      <div className="card">
        <p>Loading pair data...</p>
      </div>
    )
  }

  const currentRating = ratings[pairs[currentPairIndex].id] || 50

  return (
    <div className="evaluation-container">
      <div className="progress-indicator">
        <p>Pair {currentPairIndex + 1} of {pairs.length}</p>
      </div>

      <PairDisplay
        funder={currentPairData.funder}
        recipient={currentPairData.recipient}
      />

      <div className="rating-section card">
        <RatingSlider
          value={currentRating}
          onChange={handleRatingChange}
        />
      </div>

      <div className="form-navigation">
        <button
          type="button"
          onClick={handlePrevious}
          disabled={currentPairIndex === 0}
          className="nav-button back-button"
        >
          Previous
        </button>

        {currentPairIndex < pairs.length - 1 ? (
          <button
            type="button"
            onClick={handleNext}
            className="nav-button next-button"
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            className="nav-button submit-button"
          >
            {submitting ? "Submitting..." : "Submit Evaluations"}
          </button>
        )}
      </div>
    </div>
  )
}

export default EvaluationForm
