function About() {
  return (
    <div className="app-view">
      <div className="app-container">
        <h1 className="app-title">About <span className="prospie-highlight">prospie</span></h1>

        <div className="about-content">
          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">What is this?</span>
            </div>
            <p>
              Hello! 👋 I'm Liam. <span className="prospie-highlight">prospie</span> is my MSc Data Science dissertation project at the University of the West of England, Bristol. After eight years working in charity fundraising, I wanted to build something that actually helps with the most frustrating part of the job: working out whether your charity/project is a good match with a particular trust or foundation.
            </p>
          </section>

          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">The problem</span>
            </div>
            <p>
              I'm sure you've been there: you can spend 20 minutes plus trawling through a funder's website, annual accounts, and grants data, trying to work out if your charity is a good fit. Then you discover a tiny exclusion buried in the small print, or realise that even though they say they work across the entire UK, their accounts show that they only really fund causes in London.
            </p>
          </section>

          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">What <span className="prospie-highlight">prospie</span> does (and doesn't do)</span>
            </div>
            <p>
              <span className="prospie-highlight">prospie</span> is NOT a funder search tool. It won't help you find new prospects or generate a list of potential funders.
            </p>
            <p>
              What it DOES do: once you've identified a funder you're interested in, <span className="prospie-highlight">prospie</span> will assess how well your organisation or project aligns with them, giving you a score from 0 to 100. More importantly, it will explain its reasoning – showing you where the alignment is strong and where it's weak.
            </p>
          </section>

          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">How it works</span>
            </div>
            <p>
              I've built a database of almost 1,000 UK charitable trusts and foundations, including 32,000+ grants and 18,000+ recipients from 2001-2025. <span className="prospie-highlight">prospie</span> analyses both what funders say they support (their published criteria) and what they actually fund (their historical grants data).
            </p>
          </section>

          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">How to use it</span>
            </div>
            <ol className="about-list">
              <li>Fill in some basic details about your charity or project</li>
              <li>Enter the registered charity number of the funder you want to assess</li>
              <li>Review the alignment score and – crucially – read the reasoning behind it</li>
              <li>Use this information to make your own informed decision about whether to proceed</li>
            </ol>
          </section>

          <section className="about-section">
            <div className="question-heading">
              <span className="question-heading-text">The small print</span>
            </div>
            <p>
              This is a dissertation project, which means it's built for demonstration and learning purposes. The data is as accurate as I can make it, but it's worth double-checking anything important as some details have been extracted from charity accounts using AI. And obviously, a high score doesn't guarantee you'll get funded – there are always factors that no algorithm can capture.
            </p>
            <p>
              Unfortunately, at the moment, the project is limited to the 996 funders in the database and the availability (or lack thereof...) of their data through the Charity Commission and 360Giving. Please do try <span className="prospie-highlight">prospie</span> out but bear in mind that it's a work in progress.
            </p>
            <p>
              If you spot any issues or have feedback, I'd really appreciate hearing from you. You can reach me through my website <a href="https://liamco.io" target="_blank" class="app-link">liamco.io</a>.
            </p>
          </section>

          <div className="about-footer">
            <p>
              <span className="prospie-highlight">prospie</span> is being developed as part of the MSc Data Science programme at UWE Bristol, 2025-26. The database uses publicly available information from:
              <ul>
                  <li><a href="https://www.gov.uk/government/organisations/charity-commission" class="app-link" target="_blank">Charity Commission</a></li>
                  <li><a href="https://www.360giving.org/" class="app-link" target="_blank">360Giving</a></li>
              </ul>
              And with grateful thanks to:
              <ul>
                  <li>Jo Jeffrey, creator of <a href="https://the-list.uk" class="app-link" target="_blank">The List</a></li>
                  <li>David Kane and Christopher Damm of the <a href="https://charityclassification.org.uk/" class="app-link" target="_blank">UK Charity Classification</a> project</li>
                </ul> 
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default About
