import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="header">
      <h1>Fantasy Football Chatbot</h1>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/help">Help</Link>
      </nav>
    </header>
  );
};

export default Header;
