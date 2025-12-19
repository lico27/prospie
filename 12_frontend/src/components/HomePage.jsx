import Footer from "./Footer"

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
      </div>
      <Footer />
    </>
  )
}

export default HomePage
