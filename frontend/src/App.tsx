import { useEffect, useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Home from './pages/Home/Home';
import Results from './pages/Results/Results';
import Navbar from './components/Navbar/Navbar';
import campusBackground from './assets/images/campus-background.jpg';
import rear1888 from './assets/images/1888-Rear.jpg';
import rear1888Arial from './assets/images/1888-Arial.jpg';
import alanGilbert from './assets/images/Alan-Gilbert.jpg';
import baldwinSpencer from './assets/images/BaldwinSpencer-2.-BLDG-113.jpg';
import clockTowerCloseUp from './assets/images/ClockTowerCloseUp.jpg';
import msdMassonRdGrass from './assets/images/MSDMassonRdGrass.jpg';
import oldQuadFacingSouth from './assets/images/OldQuadFacingSouth.jpg';
import oldQuadNorthFacade from './assets/images/OldQuadNorthFacade.jpg';
import oldQuadHero from './assets/images/OldQuad_Hero.jpg';
import ormondCollegeFlag from './assets/images/OrmondCollegeFlag.jpg';
import unihouse from './assets/images/Unihouse-1.jpg';
import wilsonHall from './assets/images/WilsonHall.jpg';
import './App.css';

const backgroundOptions = [
  campusBackground,
  rear1888,
  rear1888Arial,
  alanGilbert,
  baldwinSpencer,
  clockTowerCloseUp,
  msdMassonRdGrass,
  oldQuadFacingSouth,
  oldQuadNorthFacade,
  oldQuadHero,
  ormondCollegeFlag,
  unihouse,
  wilsonHall,
] as const;
function App() {
  const location = useLocation();
  const [backgroundImage] = useState(
    () => backgroundOptions[Math.floor(Math.random() * backgroundOptions.length)],
  );

  useEffect(() => {
    window.uom?.initAllComponents();
  }, []);

  return (
    <>
      <Navbar />
      <div
        className="campus-background"
        data-testid="campus-background"
        style={{
          backgroundImage: `linear-gradient(110deg, rgba(0, 15, 70, 0.92), rgba(0, 15, 70, 0.68)), url(${backgroundImage})`,
        }}
      >
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<Results key={location.key} />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
