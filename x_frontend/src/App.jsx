import './App.css'
import { useState } from 'react'
import Navbar1 from './components/Navbar'
import HomePage from './components/HomePage'
import MultiStepForm from './components/MultiStepForm'

function App() {
  const [currentView, setCurrentView] = useState('home')
  const [formResetTrigger, setFormResetTrigger] = useState(0)

  const handleGetStarted = () => {
    setFormResetTrigger(prev => prev + 1)
    setCurrentView('app')
  }

  return (
    <>
      <Navbar1 onHomeClick={() => setCurrentView('home')} />
      {currentView === 'home' ? (
        <HomePage onGetStarted={handleGetStarted} />
      ) : (
        <MultiStepForm resetTrigger={formResetTrigger} />
      )}
    </>
  )
}

export default App
