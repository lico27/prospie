import { useState } from "react"

function RatingSlider({ value, onChange }) {
  const [localValue, setLocalValue] = useState(value || 50)

  const handleChange = (e) => {
    const newValue = parseInt(e.target.value)
    setLocalValue(newValue)
    if (onChange) {
      onChange(newValue)
    }
  }

  return (
    <div className="rating-slider-container">
      <label htmlFor="alignment-rating" className="rating-label">
        How well aligned is this funder with this recipient?
      </label>
      <div className="slider-wrapper">
        <span className="slider-label-left">Not aligned (1)</span>
        <input
          type="range"
          id="alignment-rating"
          min="1"
          max="100"
          value={localValue}
          onChange={handleChange}
          className="rating-slider"
        />
        <span className="slider-label-right">Perfectly aligned (100)</span>
      </div>
      <div className="rating-value">
        Rating: <strong>{localValue}</strong>
      </div>
    </div>
  )
}

export default RatingSlider
