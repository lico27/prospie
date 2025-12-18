function Step2ConfirmDetails({ charityData, onBack, onUseThis, onEdit }) {
  if (!charityData) {
    return <div className="loading">Loading charity data...</div>
  }

  return (
    <div className="charity-details">
      <div className="entity-column">

        <div className="instruction-box">
          <div className="instruction-icon">ℹ️</div>
          <div className="instruction-content">
            <h4 className="instruction-heading">Choose Your Details</h4>
            <p className="instruction-text">
              Below is your charity's information taken from the Charity Commission website. You can use this if you want to get started quickly, or write your own if you'd rather customise it.
            </p>
          </div>
        </div>

        <div className="entity-section">
          <h3>{charityData.recipient_name}</h3>
        </div>

        {charityData.recipient_objectives && (
          <div className="entity-section">
            <h4>Objectives</h4>
            <div className="scrollable-text-box">
              <p>{charityData.recipient_objectives}</p>
            </div>
          </div>
        )}

        {charityData.recipient_activities && (
          <div className="entity-section">
            <h4>Activities</h4>
            <div className="scrollable-text-box">
              <p>{charityData.recipient_activities}</p>
            </div>
          </div>
        )}

        {charityData.causes && charityData.causes.length > 0 && (
          <div className="entity-section">
            <h4>Causes</h4>
            <div className="tag-list">
              {charityData.causes.map((cause, idx) => (
                <span key={idx} className="tag">{cause.cause_name}</span>
              ))}
            </div>
          </div>
        )}

        {charityData.areas && charityData.areas.length > 0 && (
          <div className="entity-section">
            <h4>Geographic Areas</h4>
            <div className="tag-list">
              {charityData.areas.map((area, idx) => (
                <span key={idx} className="tag">
                  {area.area_name}
                </span>
              ))}
            </div>
          </div>
        )}

        {charityData.beneficiaries && charityData.beneficiaries.length > 0 && (
          <div className="entity-section">
            <h4>Beneficiaries</h4>
            <div className="tag-list">
              {charityData.beneficiaries.map((ben, idx) => (
                <span key={idx} className="tag">{ben.ben_name}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="step2-navigation">
        <button type="button" className="nav-button back-button" onClick={onBack}>
          Back
        </button>
        <button type="button" className="nav-button next-button" onClick={onUseThis}>
          Use This
        </button>
        <button type="button" className="nav-button edit-button" onClick={onEdit}>
          Edit My Details
        </button>
      </div>
    </div>
  )
}

export default Step2ConfirmDetails
