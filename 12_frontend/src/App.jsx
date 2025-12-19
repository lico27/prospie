import "./App.css"
import { useState } from "react"
import Navbar1 from "./components/Navbar"
import HomePage from "./components/HomePage"
import UserInput from "./components/UserInput"

function App() {
  const [currentView, setCurrentView] = useState("home")
  const [formResetTrigger, setFormResetTrigger] = useState(0)

  const handleGetStarted = () => {
    setFormResetTrigger(prev => prev + 1)
    setCurrentView("app")
  }

  return (
    <>
      <Navbar1 onHomeClick={() => setCurrentView("home")} />
      {currentView === "home" ? (
        <HomePage onGetStarted={handleGetStarted} />
      ) : (
        <UserInput resetTrigger={formResetTrigger} />
      )}
    </>
  )
}

export default App
