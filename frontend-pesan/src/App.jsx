import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HotelDetailPage from './pages/HotelDetailPage';
import PesanPage from './pages/PesanPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Singgah — Booking & Checkout */}
        <Route path="/hotel/:id" element={<HotelDetailPage />} />
        <Route path="/checkout" element={<PesanPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
