import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate, Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { Star, MapPin, Wifi, Car, Coffee, Waves, ArrowLeft, Check, ChevronRight } from 'lucide-react';
import './HotelDetailPage.css';

// Mock hotel data from hotels.json
const HOTELS_DATA = {
  HT001: {
    id: 'HT001', name: 'The Layar Private Villas', location: 'Bali', area: 'Seminyak',
    rating: 4.8, price_per_night: 1200000, room_type: 'Villa',
    facilities: ['kolam renang', 'sarapan', 'wifi', 'AC', 'parkir'],
    rooms_available: 3, address: 'Jl. Laksmana No.68, Seminyak, Bali',
    image: '/images/hotel.png',
    rooms: [
      { type: 'Standard Double', price: 450000, guests: 2, bed: 'Tempat tidur ganda', facilities: ['Free cancel'] },
      { type: 'Deluxe Pool View', price: 850000, guests: 2, bed: 'Tempat tidur ganda', facilities: ['Pemandangan'] },
    ]
  },
  HT002: {
    id: 'HT002', name: 'Kuta Central Park Hotel', location: 'Bali', area: 'Kuta',
    rating: 4.2, price_per_night: 450000, room_type: 'Deluxe',
    facilities: ['kolam renang', 'wifi', 'AC', 'restoran'],
    rooms_available: 10, address: 'Jl. Raya Kuta No.88, Kuta, Bali',
    image: '/images/hotel.png',
    rooms: [
      { type: 'Standard', price: 320000, guests: 2, bed: 'Tempat tidur ganda', facilities: ['Free cancel'] },
      { type: 'Superior', price: 450000, guests: 2, bed: 'Tempat tidur ganda', facilities: ['Sarapan gratis'] },
    ]
  },
};

const FACILITY_ICONS = {
  'kolam renang': Waves,
  'wifi': Wifi,
  'parkir': Car,
  'sarapan': Coffee,
};

const HotelDetailPage = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryParam = searchParams.get('query') || '';

  const hotel = HOTELS_DATA[id] || HOTELS_DATA.HT001;
  const [selectedRoom, setSelectedRoom] = useState(null);

  const handleSelectRoom = (room) => {
    setSelectedRoom(room);
  };

  const handleProceed = () => {
    if (selectedRoom) {
      navigate(`/pesan/checkout?hotelId=${hotel.id}&room=${encodeURIComponent(selectedRoom.type)}&price=${selectedRoom.price}&query=${encodeURIComponent(queryParam)}`);
    }
  };

  return (
    <div className="hotel-detail-page">
      {/* Pesan Navbar */}
      <header className="pesan-navbar">
        <div className="pesan-navbar-inner">
          <Link to={queryParam ? `/plan?q=${encodeURIComponent(queryParam)}` : '/'} className="pesan-back-link">
            <ArrowLeft size={18} />
            <span>Kembali</span>
          </Link>
          <nav className="pesan-nav-tabs">
            <a href="#" className="pesan-nav-tab">Hotel</a>
            <a href="#" className="pesan-nav-tab">Pesawat</a>
            <a href="#" className="pesan-nav-tab">Aktivitas</a>
          </nav>
          <div className="pesan-logo">
            <span className="text-pesan-brand">Pesan</span>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="hotel-breadcrumb">
        <div className="breadcrumb-inner">
          <span className="text-light text-caption">Beranda</span>
          <ChevronRight size={12} className="text-light" />
          <span className="text-light text-caption">Hotel</span>
          <ChevronRight size={12} className="text-light" />
          <span className="text-caption font-semibold">{hotel.name}</span>
        </div>
      </div>

      <main className="hotel-detail-main">
        {/* Image gallery */}
        <section className="hotel-gallery">
          <div className="gallery-main">
            <img src={hotel.image} alt={hotel.name} className="gallery-main-img" />
          </div>
          <div className="gallery-side">
            <div className="gallery-thumb gallery-thumb-placeholder"></div>
            <div className="gallery-thumb gallery-thumb-placeholder"></div>
          </div>
        </section>

        {/* Hotel info */}
        <section className="hotel-info-section">
          <div className="hotel-info-header">
            <div>
              <div className="hotel-info-meta">
                <Badge variant="sky">Rekomendasi AI</Badge>
                <span className="hotel-info-rating">
                  <Star size={14} fill="currentColor" /> {hotel.rating} <small>({hotel.rooms_available} reviews)</small>
                </span>
              </div>
              <h1 className="hotel-info-name">{hotel.name}</h1>
              <p className="hotel-info-location">
                <MapPin size={14} /> {hotel.area}, {hotel.location}
              </p>
            </div>
          </div>

          {/* Facilities */}
          <div className="hotel-facilities">
            {hotel.facilities.map((f, idx) => {
              const Icon = FACILITY_ICONS[f] || Check;
              return (
                <span key={idx} className="facility-tag">
                  <Icon size={14} /> {f}
                </span>
              );
            })}
          </div>
        </section>

        {/* Room selection */}
        <section className="hotel-rooms-section">
          <h2>Pilih kamar</h2>
          <div className="rooms-list">
            {hotel.rooms.map((room, idx) => (
              <div 
                key={idx} 
                className={`room-card ${selectedRoom?.type === room.type ? 'room-card-selected' : ''}`}
                onClick={() => handleSelectRoom(room)}
                role="button"
                tabIndex={0}
              >
                <div className="room-card-info">
                  <h3 className="room-card-type">{room.type}</h3>
                  <p className="room-card-details">
                    {room.guests} tamu · {room.bed} · {room.facilities.join(', ')}
                  </p>
                </div>
                <div className="room-card-price-section">
                  <span className="room-card-price-label">mulai dari</span>
                  <span className="room-card-price">Rp {room.price.toLocaleString('id-ID')}</span>
                  <Button 
                    variant={selectedRoom?.type === room.type ? 'primary' : 'outline'}
                    theme="sky"
                    size="sm"
                    onClick={(e) => { e.stopPropagation(); handleSelectRoom(room); }}
                  >
                    {selectedRoom?.type === room.type ? 'Terpilih' : 'Pilih'}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {selectedRoom && (
            <div className="room-proceed-bar fade-in">
              <div className="room-proceed-info">
                <span className="text-sm font-semibold">{selectedRoom.type}</span>
                <span className="text-sm text-sky font-bold">Rp {selectedRoom.price.toLocaleString('id-ID')}/malam</span>
              </div>
              <Button variant="primary" theme="sky" onClick={handleProceed}>
                Lanjut ke Pembayaran
              </Button>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="pesan-footer">
        <p className="text-caption text-light">© 2026 Pesan. All rights reserved. Redesigned for a better experience.</p>
      </footer>
    </div>
  );
};

export default HotelDetailPage;
