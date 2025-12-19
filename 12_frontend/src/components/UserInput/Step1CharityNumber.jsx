function Step1CharityNumber({ charityNumber, onChange }) {
  return (
    <div className="form-group">
      <label htmlFor="charityNumber">What is your registered charity number?</label>
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
