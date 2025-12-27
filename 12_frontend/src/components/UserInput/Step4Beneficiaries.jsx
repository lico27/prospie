import CheckboxGroup from "../CheckboxGroup"
import { beneficiaryOptions } from "../../data/constants"

function Step3Beneficiaries({ selectedBeneficiaries, onChange }) {
  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">Who does your project benefit?</span>
      </div>
      <CheckboxGroup
        options={beneficiaryOptions}
        selectedValues={selectedBeneficiaries}
        onChange={onChange}
      />
    </div>
  )
}

export default Step3Beneficiaries
