
import { useEffect } from "react"
import { Routes, Route, useLocation } from 'react-router-dom'
import Home from "./pages/Home/Home"
import Results from "./pages/Results/Results"
import Navbar from "./components/Navbar/Navbar"
import './App.css'

function App() {
  const location = useLocation()

  useEffect(() => {
    window.uom?.initAllComponents()
  }, [])

  return (
    <>
      <Navbar />
      <div className="campus-background">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<Results key={location.key} />} />
      </Routes>
      </div>
    </>
  )
}

export default App
