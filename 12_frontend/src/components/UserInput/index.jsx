import { useState, useEffect } from "react"
import { supabase } from "../../supabaseClient"
import ProgressIndicator from "../ProgressIndicator"
import FormNavigation from "../FormNavigation"
import Step1CharityNumber from "./Step1CharityNumber"
import Step2ConfirmDetails from "./Step2ConfirmDetails"
import Step3Areas from "./Step3Areas"
import Step4Beneficiaries from "./Step4Beneficiaries"
import Step5Causes from "./Step5Causes"
import Step6Activities from "./Step6ActivitiesObjectives"
import StepXFunderNumber from "./StepXFunderNumber"

function UserInput({ resetTrigger }) {
  const [currentStep, setCurrentStep] = useState(1)
  const [charityNumber, setCharityNumber] = useState("")
  const [charityData, setCharityData] = useState(null)
  const [selectedAreas, setSelectedAreas] = useState([])
  const [selectedBeneficiaries, setSelectedBeneficiaries] = useState([])
  const [selectedCauses, setSelectedCauses] = useState([])
  const [activities, setActivities] = useState("")
  const [objectives, setObjectives] = useState("")
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
    if (currentStep < 7) {
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
        const [areaLinks, benLinks, causeLinks] = await Promise.all([
          supabase.from("recipient_areas").select("area_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_beneficiaries").select("ben_id").eq("recipient_id", charityNumber),
          supabase.from("recipient_causes").select("cause_id").eq("recipient_id", charityNumber)
        ])

        const areaIds = areaLinks.data?.map(a => a.area_id) || []
        const benIds = benLinks.data?.map(b => b.ben_id) || []
        const causeIds = causeLinks.data?.map(c => c.cause_id) || []
        
        const [areas, beneficiaries, causes] = await Promise.all([
          areaIds.length > 0
            ? supabase.from("areas").select("area_name, area_level").in("area_id", areaIds)
            : Promise.resolve({ data: [] }),
          benIds.length > 0
            ? supabase.from("beneficiaries").select("ben_name").in("ben_id", benIds)
            : Promise.resolve({ data: [] }),
          causeIds.length > 0
            ? supabase.from("causes").select("cause_name").in("cause_id", causeIds)
            : Promise.resolve({ data: [] }),
        ])

        const enrichedData = {
          ...recipient,
          areas: areas.data || [],
          beneficiaries: beneficiaries.data || [],
          causes: causes.data || []
        }

        //pre-populate areas
        const dbAreas = areas.data?.map(a => a.area_name) || []
        setSelectedAreas(dbAreas)

        //pre-populate beneficiaries
        const dbBeneficiaries = beneficiaries.data?.map(b => b.ben_name) || []
        setSelectedBeneficiaries(dbBeneficiaries)

        //pre-populate causes
        const dbCauses = causes.data?.map(c => c.cause_name) || []
        setSelectedCauses(dbCauses)

        //pre-populate activities
        setActivities(recipient.recipient_activities || "")

        //pre-populate objectives
        setObjectives(recipient.recipient_objectives || "")

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
    setSelectedAreas([])
    setSelectedBeneficiaries([])
    setSelectedCauses([])
    setActivities("")
    setObjectives("")
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
    if (currentStep === 7) {
      handleSubmit(e)
    } else {
      handleNext()
    }
  }

  const handleStepClick = (step) => {
    //only allow backwords navigation
    if (step < currentStep) {
      setCurrentStep(step)
      setError(null)
      setFunderName(null)
      setFunderWebsite(null)
    }
  }

  return (
    <div className="app-view">
      <div className="app-container">
        <h2 className="app-title">Get your prospie score</h2>

        <ProgressIndicator
          currentStep={currentStep}
          totalSteps={7}
          onStepClick={handleStepClick}
        />

        <div className="app-form-container">
          <form onSubmit={handleFormSubmit}>
            {currentStep === 1 && (
              <Step1CharityNumber charityNumber={charityNumber} onChange={setCharityNumber} />
            )}

            {currentStep === 2 && (
              <Step2ConfirmDetails
                charityData={charityData}
                onBack={handleBack}
                onUseThis={() => setCurrentStep(7)}
                onEdit={() => setCurrentStep(3)}
              />
            )}

            {currentStep === 3 && (
              <Step3Areas
                selectedAreas={selectedAreas}
                onChange={setSelectedAreas}
              />
            )}

            {currentStep === 4 && (
              <Step4Beneficiaries
                selectedBeneficiaries={selectedBeneficiaries}
                onChange={setSelectedBeneficiaries}
              />
            )}

            {currentStep === 5 && (
              <Step5Causes
                selectedCauses={selectedCauses}
                onChange={setSelectedCauses}
              />
            )}

            {currentStep === 6 && (
              <Step6Activities
                activities={activities}
                objectives={objectives}
                onActivitiesChange={setActivities}
                onObjectivesChange={setObjectives}
              />
            )}

            {currentStep === 7 && (
              <StepXFunderNumber funderNumber={funderNumber} onChange={setFunderNumber} />
            )}

            {currentStep !== 2 && (
              <FormNavigation
                currentStep={currentStep}
                totalSteps={7}
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

export default UserInput