import Footer from './Footer'

function HomePage({ onGetStarted }) {
  return (
    <>
      <div className="hero-section">
        <div className="hero-content">
          <h1>Trusts prospecting without the guesswork</h1>
          <p>Stop trawling accounts. Check how your project aligns with funders' giving patterns in seconds.</p>
          <button className="cta-button" onClick={onGetStarted}>Get your score now</button>
        </div>
      </div>
      <div className="showcase-section">
        <div className="divider-line"></div>
        <div className="showcase-container">
          <div className="showcase-content">
            <div className="placeholder-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M9 3v18M15 3v18M3 9h18M3 15h18" />
              </svg>
            </div>
            <p className="placeholder-text">App coming soon!</p>
          </div>
        </div>
      </div>
      <Footer />
    </>
  )
}

export default HomePage
