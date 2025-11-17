function Step1CharityName({ charityName, onChange }) {
  return (
    <div className="form-group">
      <label htmlFor="charityName">What is your charity's name?</label>
      <input
        type="text"
        id="charityName"
        value={charityName}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter your charity's name"
        required
      />
    </div>
  )
}

export default Step1CharityName
