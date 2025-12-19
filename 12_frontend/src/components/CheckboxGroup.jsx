function CheckboxGroup({ options, selectedValues, onChange }) {
  const handleCheckboxChange = (option, isChecked) => {
    if (isChecked) {
      onChange([...selectedValues, option])
    } else {
      onChange(selectedValues.filter(value => value !== option))
    }
  }

  return (
    <div className="checkbox-list">
      {options.map((option, idx) => (
        <label key={idx} className="checkbox-item">
          <input
            type="checkbox"
            value={option}
            checked={selectedValues.includes(option)}
            onChange={(e) => handleCheckboxChange(option, e.target.checked)}
          />
          <span className="checkbox-label">{option}</span>
        </label>
      ))}
    </div>
  )
}

export default CheckboxGroup
