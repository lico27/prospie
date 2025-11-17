function ProgressIndicator({ currentStep, totalSteps = 4 }) {
  return (
    <div className="progress-container">
      <div className="progress-steps">
        {[...Array(totalSteps)].map((_, index) => {
          const step = index + 1
          return (
            <div key={step} className={`progress-step ${currentStep >= step ? 'active' : ''}`}>
              <div className="progress-circle">{step}</div>
              {step < totalSteps && <div className="progress-line"></div>}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ProgressIndicator
