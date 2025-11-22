import { useState } from "react"
import "./App.css"
import EvaluationForm from "./components/EvaluationForm"

function App() {
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="evaluation-section">
      <div className="evaluation-content">
        {!showForm ? (
          <>
            <h1>Thank you for agreeing to evaluate prospie!</h1>
            <div className="card instructions-card">
              <div className="instructions-section">
                <div className="section-heading">Introduction</div>
                <div className="instructions-text">
                  Hello! My name is Liam Cottrell and, as part of my MSc Data Science dissertation, I'm developing prospie – a tool designed to help trusts fundraisers assess alignment between their organisations and potential funders. To validate that prospie's scoring mechanism reflects real fundraising expertise, I need experienced fundraisers to provide comparison ratings.
                  <br /><br />
                  As you know, trusts prospecting relies heavily on professional judgment when weighing up whether a funder is worth approaching. By comparing prospie's scores with yours, I can see whether the tool captures the kind of thinking that happens in real prospect research.
                  <br /><br />
                  When I talk about "alignment," I mean how well-matched you are with a funder based on their criteria and priorities. This isn't about predicting whether an application would be successful, it's about helping you decide whether it's worth your time to apply in the first place.
                  <br /><br />
                  The final version of prospie will let you enter your own charity's details and check them against any funder in the database. For this evaluation, I'm asking you to assess three funder-recipient pairs and tell me how aligned you feel that they are.
                </div>
              </div>

              <div className="instructions-section">
                <div className="section-heading">What you'll be asked to do</div>
                <div className="instructions-text">
                  You'll see three randomly selected pairs. For each pair, you'll be shown some information about the funder and the potential recipient charity. Some pairs have more detail than others.
                  <br /><br />
                  Looking <b>only at what's on the screen</b>, please rate how well aligned you think the funder and recipient are, using a scale from 1 (not aligned) to 100 (perfectly aligned). Drag the slider left to decrease the score or right to increase it.
                </div>
              </div>

              <div className="instructions-section">
                <div className="section-heading">Important notes</div>
                <ul className="instructions-list">
                  <li>Please work from only the information shown – no need to look anything up, check websites or download accounts.</li>
                  <li>Unless otherwise marked, all information comes from the Charity Commission.</li>
                  <li>Some funders have extra details extracted from their annual accounts using AI. As you'll know, charity accounts come in all sorts of formats and the PDFs can be a bit unclear, so there may be occasional errors or formatting issues in the extracted text.</li>
                  <li>I'm interested in your professional judgment. There are no "right" or "wrong" answers.</li>
                  <li>For the best experience, use a laptop or desktop where you can see both the funder and recipient side by side. It does work on mobile too, but you'll need to scroll between them.</li>
                </ul>
              </div>

              <div className="instructions-section">
                <div className="section-heading">Time required</div>
                <div className="instructions-text">Approximately 5-10 minutes</div>
              </div>

              <div className="instructions-section">
                <div className="section-heading">Privacy</div>
                <div className="instructions-text">
                  This evaluation is completely anonymous. Only your alignment ratings (the scores you provide) will be collected and stored. No personal information will be requested or recorded, and no tracking or identification methods will be used. All data will be used solely for academic research purposes as part of my MSc dissertation at UWE Bristol.
                </div>
              </div>

              <div className="thank-you-message">
                Thank you for contributing your expertise! Your input will help develop better tools for the fundraising sector.
              </div>
            </div>
            <button onClick={() => setShowForm(true)}>Start</button>
          </>
        ) : (
          <EvaluationForm />
        )}
      </div>
    </div>
  )
}

export default App
