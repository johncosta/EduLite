// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ButtonDemo from './pages/ButtonDemo'

function App() {
  return (
    <Router>
      <Navbar />
      <div className="pt-20 px-4">
        <Routes>
          <Route path="/" element={<h1 className="text-2xl font-bold"><Home /></h1>} />
          <Route path="/about" element={<h1 className="text-2xl font-bold">About Page</h1>} />
          <Route path="/button-demo" element={<ButtonDemo />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
