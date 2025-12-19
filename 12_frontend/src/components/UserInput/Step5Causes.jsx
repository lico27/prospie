import CheckboxGroup from "../CheckboxGroup"
import { causeOptions } from "../../data/constants"

function Step3Causes({ selectedCauses, onChange }) {
  return (
    <div className="form-group">
      <label>What causes does your project support?</label>
      <CheckboxGroup
        options={causeOptions}
        selectedValues={selectedCauses}
        onChange={onChange}
      />
    </div>
  )
}

export default Step3Causes
