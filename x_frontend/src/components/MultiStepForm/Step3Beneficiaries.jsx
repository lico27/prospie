import CheckboxGroup from '../CheckboxGroup'
import { beneficiaryOptions } from '../../data/constants'

function Step3Beneficiaries({ selectedBeneficiaries, onChange }) {
  return (
    <div className="form-group">
      <label>Who does your project benefit?</label>
      <CheckboxGroup
        options={beneficiaryOptions}
        selectedValues={selectedBeneficiaries}
        onChange={onChange}
      />
    </div>
  )
}

export default Step3Beneficiaries
