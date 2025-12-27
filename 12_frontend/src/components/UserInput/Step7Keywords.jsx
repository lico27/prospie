import { useState, useEffect } from "react"
import CreatableSelect from "react-select/creatable"

function Step7Keywords({ keywords, onChange, isExtracting }) {
  const [showHint, setShowHint] = useState(false)

  const keywordOptions = keywords.map(keyword => ({
    value: keyword,
    label: keyword
  }))

  const handleChange = (selected) => {
    const keywordList = selected ? selected.map(option => option.value) : []
    onChange(keywordList)
  }

  //style
  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      backgroundColor: "rgba(26, 22, 37, 0.6)",
      borderColor: state.isFocused ? "rgba(111, 163, 168, 0.6)" : "rgba(142, 125, 179, 0.3)",
      borderRadius: "8px",
      padding: "0.25rem",
      boxShadow: state.isFocused ? "0 0 0 3px rgba(111, 163, 168, 0.1)" : "none",
      transition: "all 0.3s ease",
      "&:hover": {
        borderColor: "rgba(142, 125, 179, 0.5)"
      }
    }),
    menu: (provided) => ({
      ...provided,
      backgroundColor: "rgba(42, 38, 54, 0.95)",
      border: "1px solid rgba(142, 125, 179, 0.3)",
      borderRadius: "8px",
      backdropFilter: "blur(10px)",
      boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)"
    }),
    menuList: (provided) => ({
      ...provided,
      padding: "0.5rem",
      maxHeight: "300px",
      "::-webkit-scrollbar": {
        width: "8px"
      },
      "::-webkit-scrollbar-track": {
        background: "rgba(26, 22, 37, 0.6)"
      },
      "::-webkit-scrollbar-thumb": {
        background: "rgba(142, 125, 179, 0.3)",
        borderRadius: "4px"
      },
      "::-webkit-scrollbar-thumb:hover": {
        background: "rgba(142, 125, 179, 0.5)"
      }
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected
        ? "rgba(142, 125, 179, 0.3)"
        : state.isFocused
        ? "rgba(142, 125, 179, 0.15)"
        : "transparent",
      color: state.isSelected ? "#dcd3ed" : "#c9c0de",
      padding: "0.6rem 0.75rem",
      cursor: "pointer",
      borderRadius: "4px",
      fontSize: "0.9rem",
      transition: "all 0.2s ease",
      "&:active": {
        backgroundColor: "rgba(142, 125, 179, 0.25)"
      }
    }),
    multiValue: (provided) => ({
      ...provided,
      backgroundColor: "rgba(142, 125, 179, 0.2)",
      border: "1px solid rgba(142, 125, 179, 0.3)",
      borderRadius: "6px"
    }),
    multiValueLabel: (provided) => ({
      ...provided,
      color: "#dcd3ed",
      fontSize: "0.85rem",
      padding: "0.3rem 0.5rem"
    }),
    multiValueRemove: (provided) => ({
      ...provided,
      color: "#c9c0de",
      ":hover": {
        backgroundColor: "rgba(220, 92, 92, 0.3)",
        color: "#ffb3b3",
        borderRadius: "0 4px 4px 0"
      }
    }),
    placeholder: (provided) => ({
      ...provided,
      color: "rgba(201, 192, 222, 0.4)",
      fontSize: "0.9rem"
    }),
    input: (provided) => ({
      ...provided,
      color: "#ffffff"
    }),
    noOptionsMessage: (provided) => ({
      ...provided,
      color: "#c9c0de",
      fontSize: "0.9rem",
      padding: "0.75rem"
    })
  }

  return (
    <div className="form-group">
      <div className="question-heading">
        <span className="question-heading-text">Review Your Keywords</span>
      </div>
      <p className="form-helper-text">
        These keywords have been automatically extracted from your areas, beneficiaries, causes, activities, and objectives.
        You can add (or delete) keywords below.
      </p>

      <div className="hint-toggle" onClick={() => setShowHint(!showHint)}>
        <span className="hint-icon">{showHint ? "▼" : "▶"}</span>
        <span className="hint-toggle-text">What are keywords and how do they help?</span>
      </div>

      {showHint && (
        <div className="hint-box">
          <p className="hint-intro">
            Keywords are specific terms and phrases that describe your charity's work. prospie uses them as part of the calculation of your alignment score with your selected funder.
          </p>
          <div className="hint-example">
            <p><strong>How it works:</strong></p>
            <ul className="hint-list">
              <li>prospie has automatically extracted keywords using <a href="https://charityclassification.org.uk/" target="_blank" rel="noopener noreferrer" className="app-link">UKCAT charity classifications</a> and your input</li>
              <li>More specific keywords (like "care-experienced young people") offer more value than broad terms (like "education")</li>
              <li>You can remove irrelevant keywords or add additional ones that better describe your work</li>
            </ul>
          </div>
        </div>
      )}

      {isExtracting ? (
        <div className="loading" style={{ textAlign: "left", padding: "1rem 0" }}>
          Extracting keywords from your data...
        </div>
      ) : (
        <CreatableSelect
          isMulti
          value={keywordOptions}
          onChange={handleChange}
          options={[]}
          placeholder="Your extracted keywords will appear here. Type to add custom keywords..."
          styles={customStyles}
          className="react-select-container"
          classNamePrefix="react-select"
          formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
        />
      )}
    </div>
  )
}

export default Step7Keywords
