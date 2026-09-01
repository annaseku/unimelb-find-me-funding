
import { useEffect } from "react"
import Home from "./pages/Home/Home"
import Navbar from "./components/Navbar/Navbar"

function App() {

  useEffect(() => {
    window.uom?.initAllComponents()
  }, [])

  return (
    <>
      <Navbar />
      <Home />
    </>
  )
}

export default App
