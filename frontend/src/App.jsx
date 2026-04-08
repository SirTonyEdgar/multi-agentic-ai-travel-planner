import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import PlannerPage from './pages/PlannerPage';
import HotelDetailPage from './pages/HotelDetailPage';
import PesanPage from './pages/PesanPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Jalan — Travel Planner */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/plan" element={<PlannerPage />} />
        
        {/* Pesan — Booking */}
        <Route path="/pesan/hotel/:id" element={<HotelDetailPage />} />
        <Route path="/pesan/checkout" element={<PesanPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
