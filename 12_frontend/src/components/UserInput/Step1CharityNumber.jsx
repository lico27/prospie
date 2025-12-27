function Step1CharityNumber({ charityNumber, onChange }) {
  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">What is your registered charity number?</span>
      </div>
      <input
        type="text"
        id="charityNumber"
        value={charityNumber}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter your charity number"
        pattern="[0-9]*"
        inputMode="numeric"
        required
      />
    </div>
  )
}

export default Step1CharityNumber
