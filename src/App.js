import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Help from "./components/Help";
import Header from "./components/Header";

const App = () => {
  return (
    <div className="app-container">
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/help" element={<Help />} />
      </Routes>
    </div>
  );
};

export default App;
