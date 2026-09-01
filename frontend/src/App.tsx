
import { useEffect } from "react"
import { Routes, Route } from 'react-router-dom'
import Home from "./pages/Home/Home"
import Results from "./pages/Results/Results"
import Navbar from "./components/Navbar/Navbar"

function App() {

  useEffect(() => {
    window.uom?.initAllComponents()
  }, [])

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </>
  )
}

export default App
