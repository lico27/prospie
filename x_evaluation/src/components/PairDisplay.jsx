function PairDisplay({ funder, recipient }) {
  if (!funder || !recipient) {
    return <div className="loading">Loading pair data...</div>
  }

  return (
    <div className="pair-display">
      <div className="pair-columns">
        {/* Funder Column */}
        <div className="entity-column funder-column">
          <h2 className="entity-title">Funder</h2>

          <div className="entity-section">
            <h3>{funder.name}</h3>
          </div>

          {funder.activities && (
            <div className="entity-section">
              <h4>Activities</h4>
              <div className="scrollable-text-box">
                <p>{funder.activities}</p>
              </div>
            </div>
          )}

          {funder.objectives && (
            <div className="entity-section">
              <h4>Objectives</h4>
              <div className="scrollable-text-box">
                <p>{funder.objectives}</p>
              </div>
            </div>
          )}

          {funder.objectives_activities && (
            <div className="entity-section">
              <h4>Objectives & Activities</h4>
              <h5>(Extracted From Accounts)</h5>
              <div className="scrollable-text-box">
                <p>{funder.objectives_activities}</p>
              </div>
            </div>
          )}

          {funder.achievements_performance && (
            <div className="entity-section">
              <h4>Achievements & Performance</h4>
              <h5>(Extracted From Accounts)</h5>
              <div className="scrollable-text-box">
                <p>{funder.achievements_performance}</p>
              </div>
            </div>
          )}

          {funder.grant_policy && (
            <div className="entity-section">
              <h4>Grant Policy</h4>
              <h5>(Extracted From Accounts)</h5>
              <div className="scrollable-text-box">
                <p>{funder.grant_policy}</p>
              </div>
            </div>
          )}

          {funder.areas && funder.areas.length > 0 && (
            <div className="entity-section">
              <h4>Geographic Areas</h4>
              <div className="tag-list">
                {funder.areas.map((area, idx) => (
                  <span key={idx} className="tag">
                    {area.area_name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {funder.causes && funder.causes.length > 0 && (
            <div className="entity-section">
              <h4>Causes</h4>
              <div className="tag-list">
                {funder.causes.map((cause, idx) => (
                  <span key={idx} className="tag">{cause.cause_name}</span>
                ))}
              </div>
            </div>
          )}

          {funder.beneficiaries && funder.beneficiaries.length > 0 && (
            <div className="entity-section">
              <h4>Beneficiaries</h4>
              <div className="tag-list">
                {funder.beneficiaries.map((ben, idx) => (
                  <span key={idx} className="tag">{ben.ben_name}</span>
                ))}
              </div>
            </div>
          )}

          {funder.grants && funder.grants.length > 0 && (() => {
            // Get the most recent year
            const mostRecentYear = Math.max(...funder.grants.map(g => g.year || 0).filter(y => y > 0))
            const recentGrants = funder.grants.filter(g => g.year === mostRecentYear)

            return (
              <div className="entity-section">
                <h4>Recent Grants - {mostRecentYear}</h4>
                <h5>(Extracted From Accounts)</h5>
                <div className="grants-table">
                  <div className="grants-table-header">
                    <div className="grants-col-year">Year</div>
                    <div className="grants-col-recipient">Recipient</div>
                    <div className="grants-col-amount">Amount</div>
                  </div>
                  <div className="grants-table-body">
                    {recentGrants.map((grant, idx) => (
                      <div key={idx} className="grants-table-row">
                        <div className="grants-col-year">{grant.year || '—'}</div>
                        <div className="grants-col-recipient">{grant.recipient_name || 'Unknown'}</div>
                        <div className="grants-col-amount">
                          {grant.amount ? `£${grant.amount.toLocaleString()}` : '—'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })()}

          <div className="entity-section">
            <h4>Financial Info (Latest Year)</h4>
            <p>Income: £{funder.income_latest ? Number(funder.income_latest).toLocaleString() : 'N/A'}</p>
            <p>Expenditure: £{funder.expenditure_latest ? Number(funder.expenditure_latest).toLocaleString() : 'N/A'}</p>
          </div>

          <div className="entity-section">
            <h4>
              Is this funder on{' '}
              <a href="https://the-list.uk" target="_blank" rel="noopener noreferrer" className="the-list-link">
                The List
              </a>
              ?
            </h4>
            <p className="list-status">
              {funder.is_on_list ? 'Yes' : 'No'}
            </p>
          </div>

          {funder.is_potential_sbf && (
            <div className="warning-box">
              <span className="warning-icon">⚠️</span>
              <p>This could be a single-beneficiary funder. Data suggests that they may only support one cause (e.g a school or a church).</p>
            </div>
          )}

          {funder.is_nua && (
            <div className="warning-box">
              <span className="warning-icon">⚠️</span>
              <p>This funder has potentially indicated that they do not accept unsolicited applications.</p>
            </div>
          )}
        </div>

        {/* Recipient Column */}
        <div className="entity-column recipient-column">
          <h2 className="entity-title">Applicant Charity</h2>

          <div className="entity-section">
            <h3>{recipient.recipient_name}</h3>
          </div>

          {recipient.recipient_activities && (
            <div className="entity-section">
              <h4>Activities</h4>
              <div className="scrollable-text-box">
                <p>{recipient.recipient_activities}</p>
              </div>
            </div>
          )}

          {recipient.areas && recipient.areas.length > 0 && (
            <div className="entity-section">
              <h4>Geographic Areas</h4>
              <div className="tag-list">
                {recipient.areas.map((area, idx) => (
                  <span key={idx} className="tag">
                    {area.area_name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {recipient.causes && recipient.causes.length > 0 && (
            <div className="entity-section">
              <h4>Causes</h4>
              <div className="tag-list">
                {recipient.causes.map((cause, idx) => (
                  <span key={idx} className="tag">{cause.cause_name}</span>
                ))}
              </div>
            </div>
          )}

          {recipient.beneficiaries && recipient.beneficiaries.length > 0 && (
            <div className="entity-section">
              <h4>Beneficiaries</h4>
              <div className="tag-list">
                {recipient.beneficiaries.map((ben, idx) => (
                  <span key={idx} className="tag">{ben.ben_name}</span>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}

export default PairDisplay
