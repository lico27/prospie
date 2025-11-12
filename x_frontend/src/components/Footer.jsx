import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-brand">
            <h3>prospie</h3>
            <p>Trusts prospecting without the guesswork</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#about">About</a>
            </div>
            <div className="footer-column">
              <h4>Support</h4>
              <a href="#help">Help</a>
              <a href="#contact">Contact</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 prospie. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
