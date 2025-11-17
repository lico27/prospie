import { toTitleCase } from '../utils/helpers'

function ResultDisplay({ funderName, funderWebsite, onReset }) {
  return (
    <div className="result">
      <p><strong>Funder Name:</strong> {toTitleCase(funderName)}</p>
      {funderWebsite && (
        <p><strong>Website:</strong> <a href={funderWebsite} target="_blank" rel="noopener noreferrer">{funderWebsite}</a></p>
      )}
      <button className="reset-button" onClick={onReset}>Search Again</button>
    </div>
  )
}

export default ResultDisplay
