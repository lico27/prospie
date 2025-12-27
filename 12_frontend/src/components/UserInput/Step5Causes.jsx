import CheckboxGroup from "../CheckboxGroup"
import { causeOptions } from "../../data/constants"

function Step3Causes({ selectedCauses, onChange }) {
  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">What causes does your project support?</span>
      </div>
      <CheckboxGroup
        options={causeOptions}
        selectedValues={selectedCauses}
        onChange={onChange}
      />
    </div>
  )
}

export default Step3Causes
