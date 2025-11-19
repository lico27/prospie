import { useState } from 'react'

function EvaluationForm() {
  const [answer, setAnswer] = useState('')

  return (
    <div className="card">
      <form className="evaluation-form">
        <div className="form-group">
          <label htmlFor="question1">Question 1</label>
          <input
            type="text"
            id="question1"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Your answer here..."
          />
        </div>
      </form>
    </div>
  )
}

export default EvaluationForm
