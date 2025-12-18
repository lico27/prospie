import { useState, useEffect } from "react"
import { supabase } from "../../supabaseClient"
import ProgressIndicator from "../ProgressIndicator"
import FormNavigation from "../FormNavigation"
import ResultDisplay from "../ResultDisplay"
import Step1CharityNumber from "./Step1CharityNumber"
import Step2Beneficiaries from "./Step2Beneficiaries"
import Step3Causes from "./Step3Causes"
import Step4FunderNumber from "./Step4FunderNumber"

function MultiStepForm({ resetTrigger }) {
  const [currentStep, setCurrentStep] = useState(1)
  const [charityNumber, setCharityNumber] = useState("")
  const [selectedBeneficiaries, setSelectedBeneficiaries] = useState([])
  const [selectedCauses, setSelectedCauses] = useState([])
  const [funderNumber, setFunderNumber] = useState("")
  const [funderName, setFunderName] = useState(null)
  const [funderWebsite, setFunderWebsite] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setFunderName(null)
    setFunderWebsite(null)

    try {
      const { data, error } = await supabase
        .from("funders")
        .select("name, website")
        .eq("registered_num", funderNumber)
        .single()

      if (error) throw error

      if (data) {
        setFunderName(data.name)
        setFunderWebsite(data.website)
      }
    } catch (err) {
      if (err.message.includes("Cannot coerce the result to a single JSON object")) {
        setError("Please enter a valid registered charity number")
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleNext = async () => {
    if (currentStep < 4) {
      if (currentStep === 1) {
        await validateCharityNumber()
      } else {
        setCurrentStep(currentStep + 1)
        setError(null)
        setFunderName(null)
        setFunderWebsite(null)
      }
    }
  }

  const validateCharityNumber = async () => {
    if (!charityNumber) {
      setError("Please enter a charity number")
      return
    }

    if (!/^\d+$/.test(charityNumber)) {
      setError("Charity number must contain only numbers")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase
        .from("recipients")
        .select("recipient_id")
        .eq("recipient_id", charityNumber)
        .single()

      if (error) throw error

      if (data) {
        setCurrentStep(currentStep + 1)
        setError(null)
      }
    } catch (err) {
      if (err.message.includes("Cannot coerce the result to a single JSON object")) {
        setError("Charity number not found. Please enter a valid registered charity number.")
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      setError(null)
      setFunderName(null)
      setFunderWebsite(null)
    }
  }

  const handleReset = () => {
    setCurrentStep(1)
    setCharityNumber("")
    setSelectedBeneficiaries([])
    setSelectedCauses([])
    setFunderNumber("")
    setFunderName(null)
    setFunderWebsite(null)
    setError(null)
  }

  useEffect(() => {
    handleReset()
  }, [resetTrigger])

  const handleFormSubmit = (e) => {
    e.preventDefault()
    if (currentStep === 4) {
      handleSubmit(e)
    } else {
      handleNext()
    }
  }

  return (
    <div className="app-view">
      <div className="app-container">
        <h2 className="app-title">Get your prospie score</h2>

        <ProgressIndicator currentStep={currentStep} />

        <div className="app-form-container">
          <form onSubmit={handleFormSubmit}>
            {currentStep === 1 && (
              <Step1CharityNumber charityNumber={charityNumber} onChange={setCharityNumber} />
            )}

            {currentStep === 2 && (
              <Step2Beneficiaries
                selectedBeneficiaries={selectedBeneficiaries}
                onChange={setSelectedBeneficiaries}
              />
            )}

            {currentStep === 3 && (
              <Step3Causes
                selectedCauses={selectedCauses}
                onChange={setSelectedCauses}
              />
            )}

            {currentStep === 4 && (
              <Step4FunderNumber funderNumber={funderNumber} onChange={setFunderNumber} />
            )}

            <FormNavigation
              currentStep={currentStep}
              totalSteps={4}
              onBack={handleBack}
              onNext={handleNext}
              onSubmit={handleSubmit}
              loading={loading}
            />
          </form>

          {funderName && (
            <ResultDisplay
              funderName={funderName}
              funderWebsite={funderWebsite}
              onReset={handleReset}
            />
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MultiStepForm
