import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import './Navbar.css';

function Navbar1({ onHomeClick }) {
  const handleHomeClick = (e) => {
    e.preventDefault();
    if (onHomeClick) {
      onHomeClick();
    }
  };

  return (
    <Navbar expand="lg" className="glass-navbar" data-bs-theme="dark">
      <Container>
        <Navbar.Brand href="#home" onClick={handleHomeClick}>🔎</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="w-100 justify-content-evenly">
            <Nav.Link href="#home" onClick={handleHomeClick}>Home</Nav.Link>
            <Nav.Link href="#about">About</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Navbar1;