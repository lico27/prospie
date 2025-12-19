function Step4FunderNumber({ funderNumber, onChange }) {
  return (
    <div className="form-group">
      <label htmlFor="funderNumber">Funder's Registered Charity Number</label>
      <input
        type="text"
        id="funderNumber"
        value={funderNumber}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter funder's registered charity number"
        required
      />
    </div>
  )
}

export default Step4FunderNumber
