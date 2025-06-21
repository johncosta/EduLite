// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import BackToTopButton from "./components/common/BackToTopButton";
import ButtonDemo from "./pages/ButtonDemo";
import AboutPage from "./pages/AboutPage";

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/button-demo" element={<ButtonDemo />} />
          </Routes>
        </main>
        <Footer />
        <BackToTopButton />
      </div>
    </Router>
  );
}

export default App;
