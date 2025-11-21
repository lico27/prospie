import { useState } from "react"
import "./App.css"
import EvaluationForm from "./components/EvaluationForm"

function App() {
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="evaluation-section">
      <div className="evaluation-content">
        {!showForm ? (
          <>
            <h1>Thank you for agreeing to evaluate prospie!</h1>
            <div className="card">
              <p>Instructions will go here</p>
            </div>
            <button onClick={() => setShowForm(true)}>Start</button>
          </>
        ) : (
          <EvaluationForm />
        )}
      </div>
    </div>
  )
}

export default App
