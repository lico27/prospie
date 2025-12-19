function FormNavigation({ currentStep, totalSteps, onBack, onNext, onSubmit, loading }) {
  const isFirstStep = currentStep === 1
  const isLastStep = currentStep === totalSteps

  return (
    <div className="form-navigation">
      {!isFirstStep && (
        <button type="button" className="nav-button back-button" onClick={onBack}>
          Back
        </button>
      )}
      {isLastStep ? (
        <button type="submit" className="nav-button submit-button" disabled={loading}>
          {loading ? "Searching..." : "Submit"}
        </button>
      ) : (
        <button type="submit" className="nav-button next-button">
          Next
        </button>
      )}
    </div>
  )
}

export default FormNavigation
