import "./App.css"
import { useState } from "react"
import Navbar1 from "./components/Navbar"
import HomePage from "./components/HomePage"
import UserInput from "./components/UserInput"
import About from "./components/About"

function App() {
  const [currentView, setCurrentView] = useState("home")
  const [formResetTrigger, setFormResetTrigger] = useState(0)

  const handleGetStarted = () => {
    setFormResetTrigger(prev => prev + 1)
    setCurrentView("app")
  }

  const renderView = () => {
    switch (currentView) {
      case "home":
        return <HomePage onGetStarted={handleGetStarted} />
      case "about":
        return <About />
      case "app":
        return <UserInput resetTrigger={formResetTrigger} />
      default:
        return <HomePage onGetStarted={handleGetStarted} />
    }
  }

  return (
    <>
      <Navbar1
        onHomeClick={() => setCurrentView("home")}
        onAboutClick={() => setCurrentView("about")}
      />
      {renderView()}
    </>
  )
}

export default App
