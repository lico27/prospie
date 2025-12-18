import { useState, useEffect } from "react"
import { supabase } from "../../supabaseClient"
import ProgressIndicator from "../ProgressIndicator"
import FormNavigation from "../FormNavigation"
import ResultDisplay from "../ResultDisplay"
import Step1CharityNumber from "./Step1CharityNumber"
import Step2ConfirmDetails from "./Step2ConfirmDetails"
import Step3Beneficiaries from "./Step3Beneficiaries"
import Step3Causes from "./Step3Causes"
import Step4FunderNumber from "./Step4FunderNumber"

function MultiStepForm({ resetTrigger }) {
  const [currentStep, setCurrentStep] = useState(1)
  const [charityNumber, setCharityNumber] = useState("")
  const [charityData, setCharityData] = useState(null)
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
    if (currentStep < 5) {
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
      const { data: recipient, error } = await supabase
        .from("recipients")
        .select("*")
        .eq("recipient_id", charityNumber)
        .single()

      if (error) throw error

      if (recipient) {
        const [areaLinks, causeLinks, benLinks] = await Promise.all([
          supabase.from("recipient_areas").select("area_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_causes").select("cause_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_beneficiaries").select("ben_id").eq("recipient_id", charityNumber)
        ])

        const areaIds = areaLinks.data?.map(a => a.area_id) || []
        const causeIds = causeLinks.data?.map(c => c.cause_id) || []
        const benIds = benLinks.data?.map(b => b.ben_id) || []

        const [areas, causes, beneficiaries] = await Promise.all([
          areaIds.length > 0
            ? supabase.from("areas").select("area_name, area_level").in("area_id", areaIds)
            : Promise.resolve({ data: [] }),
          causeIds.length > 0
            ? supabase.from("causes").select("cause_name").in("cause_id", causeIds)
            : Promise.resolve({ data: [] }),
          benIds.length > 0
            ? supabase.from("beneficiaries").select("ben_name").in("ben_id", benIds)
            : Promise.resolve({ data: [] })
        ])

        const enrichedData = {
          ...recipient,
          areas: areas.data || [],
          causes: causes.data || [],
          beneficiaries: beneficiaries.data || []
        }

        // Pre-populate selected beneficiaries from database
        const dbBeneficiaries = beneficiaries.data?.map(b => b.ben_name) || []
        setSelectedBeneficiaries(dbBeneficiaries)

        // Pre-populate selected causes from database
        const dbCauses = causes.data?.map(c => c.cause_name) || []
        setSelectedCauses(dbCauses)

        setCharityData(enrichedData)
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
    setCharityData(null)
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
    if (currentStep === 5) {
      handleSubmit(e)
    } else {
      handleNext()
    }
  }

  return (
    <div className="app-view">
      <div className="app-container">
        <h2 className="app-title">Get your prospie score</h2>

        <ProgressIndicator currentStep={currentStep} totalSteps={5} />

        <div className="app-form-container">
          <form onSubmit={handleFormSubmit}>
            {currentStep === 1 && (
              <Step1CharityNumber charityNumber={charityNumber} onChange={setCharityNumber} />
            )}

            {currentStep === 2 && (
              <Step2ConfirmDetails
                charityData={charityData}
                onBack={handleBack}
                onUseThis={() => setCurrentStep(5)}
                onEdit={() => setCurrentStep(3)}
              />
            )}

            {currentStep === 3 && (
              <Step3Beneficiaries
                selectedBeneficiaries={selectedBeneficiaries}
                onChange={setSelectedBeneficiaries}
              />
            )}

            {currentStep === 4 && (
              <Step3Causes
                selectedCauses={selectedCauses}
                onChange={setSelectedCauses}
              />
            )}

            {currentStep === 5 && (
              <Step4FunderNumber funderNumber={funderNumber} onChange={setFunderNumber} />
            )}

            {currentStep !== 2 && (
              <FormNavigation
                currentStep={currentStep}
                totalSteps={5}
                onBack={handleBack}
                onNext={handleNext}
                onSubmit={handleSubmit}
                loading={loading}
              />
            )}
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
