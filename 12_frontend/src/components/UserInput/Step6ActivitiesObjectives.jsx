import { useState } from "react"

function Step6ActivitiesObjectives({ activities, objectives, onActivitiesChange, onObjectivesChange }) {
  const [showHint, setShowHint] = useState(false)

  return (
    <>
      <h3 className="section-main-heading">Activities & Objectives</h3>
      <p className="form-helper-text">These are your activities and objectives as described on the Charity Commission website. Use the text boxes to edit or add to them if required.</p>

      <div className="hint-toggle" onClick={() => setShowHint(!showHint)}>
        <span className="hint-icon">{showHint ? "▼" : "▶"}</span>
        <span className="hint-toggle-text">Writing tips and examples</span>
      </div>

      {showHint && (
        <div className="hint-box">
          <p className="hint-intro">Please be specific about who you help, what you do, and the outcomes you're working towards. Avoid generic buzzwords - concrete details will help prospie calculate your score more accurately.</p>

          <div className="hint-examples-grid">
            <div className="hint-column">
              <h4 className="hint-section-title">Activities</h4>
              <div className="hint-example hint-good">
                <span className="hint-label">✅ Good:</span>
                <p>"We provide hot meals and social activities for isolated older people in rural villages, focusing on reducing loneliness through community cafes and volunteer befriending schemes."</p>
              </div>
              <div className="hint-example hint-bad">
                <span className="hint-label">❌ Vague:</span>
                <p>"We help elderly people."</p>
              </div>
              <div className="hint-example hint-bad">
                <span className="hint-label">❌ Generic:</span>
                <p>"We are committed to delivering excellence in high-quality services that make a meaningful difference to the lives of vulnerable members of our community through our innovative and holistic approach."</p>
              </div>
            </div>

            <div className="hint-column">
              <h4 className="hint-section-title">Objectives</h4>
              <div className="hint-example hint-good">
                <span className="hint-label">✅ Good:</span>
                <p>"To advance education of care-experienced young people aged 16-25 through one-to-one mentoring and work experience placements in creative industries."</p>
              </div>
              <div className="hint-example hint-bad">
                <span className="hint-label">❌ Generic:</span>
                <p>"To help young people reach their potential."</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Activities Section */}
      <div className="form-subsection">
        <h4 className="form-subheading">What activities does your charity carry out?</h4>
        <textarea
          value={activities}
          onChange={(e) => onActivitiesChange(e.target.value)}
          placeholder="Enter your charity's activities..."
          rows={8}
          className="form-textarea"
        />
      </div>

      {/* Objectives Section */}
      <div className="form-subsection">
        <h4 className="form-subheading">What are your charity's objectives?</h4>
        <textarea
          value={objectives}
          onChange={(e) => onObjectivesChange(e.target.value)}
          placeholder="Enter your charity's objectives..."
          rows={8}
          className="form-textarea"
        />
      </div>
    </>
  )
}

export default Step6ActivitiesObjectives
