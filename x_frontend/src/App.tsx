import React from 'react'
import './App.css'
import prospieCharacter from './assets/prospie-character.png'

function App(): React.JSX.Element {
  return (
    <div className="landing-container">
      <img src={prospieCharacter} alt="Prospie Character" className="character" />
      <div className="speech-bubble">
        <h1>Hi, I'm prospie!</h1>
        <p>Stay tuned! We're launching soon.</p>
      </div>
    </div>
  )
}

export default App
