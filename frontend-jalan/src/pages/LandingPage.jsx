import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DestinationCard from '../components/ui/DestinationCard';
import { Sparkles, MapPin, Search, Compass, UtensilsCrossed, Landmark } from 'lucide-react';
import './LandingPage.css';

const PESAN_URL = import.meta.env.VITE_PESAN_URL || 'http://localhost:5174';

const DESTINATIONS = [
  {
    name: 'Bali',
    image: '/images/bali.png',
    activities: 8,
    rating: 4.7,
    query: 'Saya mau liburan ke Bali, carikan rekomendasi wisata, kuliner, dan hotel'
  },
  {
    name: 'Yogyakarta',
    image: '/images/yogyakarta.png',
    activities: 4,
    rating: 4.8,
    query: 'Saya mau ke Yogyakarta, carikan rekomendasi wisata, kuliner, dan hotel'
  },
  {
    name: 'Lombok',
    image: '/images/lombok.png',
    activities: 2,
    rating: 4.8,
    query: 'Saya mau ke Lombok, carikan rekomendasi wisata dan hotel'
  },
];

const CATEGORIES = [
  { label: 'Wisata', icon: Compass, query: 'Rekomendasikan tempat wisata populer di Bali' },
  { label: 'Kuliner', icon: UtensilsCrossed, query: 'Rekomendasikan tempat makan enak di Bali' },
  { label: 'Ibadah', icon: Landmark, query: 'Ada masjid apa saja di Bali?' },
];

const LandingPage = () => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/plan?q=${encodeURIComponent(query)}`);
    }
  };

  const handleDestination = (dest) => {
    navigate(`/plan?q=${encodeURIComponent(dest.query)}`);
  };

  const handleCategory = (cat) => {
    navigate(`/plan?q=${encodeURIComponent(cat.query)}`);
  };

  return (
    <div className="landing-page">
      {/* ── Navbar ── */}
      <header className="navbar" id="navbar">
        <div className="navbar-inner">
          <div className="logo" id="logo">
            <span className="text-kelana">Kelana</span>
          </div>
          <nav className="nav-links" id="nav-links">
            <a href="#destinasi">Eksplor</a>
            <a href="#kategori">Kategori</a>
          </nav>
          <div className="nav-actions">
            <Button variant="ghost" theme="warm" size="sm">Masuk</Button>
            <Button variant="primary" theme="warm" size="sm">Daftar</Button>
          </div>
        </div>
      </header>

      {/* ── Hero ── */}
      <main className="hero-section" id="hero-section">
        <div className="hero-content fade-in-up">
          <Badge variant="warm" icon={Sparkles}>Rekomendasi AI</Badge>

          <h1 className="hero-title">
            Rencanakan perjalananmu
          </h1>
          <p className="hero-subtitle">
            Destinasi populer minggu ini
          </p>
          <p className="hero-desc">
            Ceritakan rencana perjalananmu — tujuan, budget, durasi trip, dan agen AI kami akan merancangkan itinerary lengkap untukmu.
          </p>

          <form onSubmit={handleSearch} className="search-form" id="search-form">
            <div className="search-card">
              <div className="search-input-wrapper">
                <MapPin className="search-icon" size={18} />
                <input
                  type="text"
                  id="search-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Mau jalan-jalan ke mana minggu ini?"
                  className="search-input"
                  autoComplete="off"
                />
              </div>
              <Button type="submit" variant="primary" theme="warm" icon={Search}>
                Buat Rencana
              </Button>
            </div>
          </form>

          {/* Quick suggestions */}
          <div className="hero-suggestions">
            <span className="suggestion-label">Populer:</span>
            {['Bali 3 Hari', 'Jogja Budget', 'Lombok Snorkeling'].map((s, i) => (
              <button
                key={i}
                className="suggestion-chip"
                onClick={() => {
                  setQuery(s === 'Bali 3 Hari'
                    ? 'Saya mau liburan ke Bali 3 hari dari Jakarta, carikan tiket termurah, hotel budget 600 ribu, dan rekomendasi wisata'
                    : s === 'Jogja Budget'
                    ? 'Saya mau ke Yogyakarta budget hemat, carikan hotel murah dan wisata gratis'
                    : 'Saya mau snorkeling di Lombok, carikan tiket dan rekomendasi wisata');
                  navigate(`/plan?q=${encodeURIComponent(
                    s === 'Bali 3 Hari'
                    ? 'Saya mau liburan ke Bali 3 hari dari Jakarta, carikan tiket termurah, hotel budget 600 ribu, dan rekomendasi wisata'
                    : s === 'Jogja Budget'
                    ? 'Saya mau ke Yogyakarta budget hemat, carikan hotel murah dan wisata gratis'
                    : 'Saya mau snorkeling di Lombok, carikan tiket dan rekomendasi wisata'
                  )}`);
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </main>

      {/* ── Destinations ── */}
      <section className="section-destinations" id="destinasi">
        <div className="section-container">
          <div className="section-header fade-in-up">
            <h2>Destinasi Populer</h2>
            <p className="text-muted">Jelajahi keindahan Indonesia yang menakjubkan</p>
          </div>
          <div className="destinations-grid">
            {DESTINATIONS.map((dest, idx) => (
              <DestinationCard
                key={idx}
                name={dest.name}
                image={dest.image}
                activities={dest.activities}
                rating={dest.rating}
                onClick={() => handleDestination(dest)}
                className="fade-in-up"
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── Categories ── */}
      <section className="section-categories" id="kategori">
        <div className="section-container">
          <div className="section-header fade-in-up">
            <h2>Kategori Aktivitas</h2>
            <p className="text-muted">Temukan pengalaman sesuai minatmu</p>
          </div>
          <div className="categories-grid">
            {CATEGORIES.map((cat, idx) => (
              <div
                key={idx}
                className="category-card fade-in-up"
                onClick={() => handleCategory(cat)}
                role="button"
                tabIndex={0}
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="category-icon-wrapper">
                  <cat.icon size={24} />
                </div>
                <h3 className="category-name">{cat.label}</h3>
                <p className="category-desc">
                  {cat.label === 'Wisata' && 'Pantai, candi, sawah terasering, dan destinasi ikonik lainnya'}
                  {cat.label === 'Kuliner' && 'Warung legendaris, seafood, jajanan khas, dan hidangan lokal'}
                  {cat.label === 'Ibadah' && 'Masjid bersejarah, pura, dan tempat ibadah indah'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer" id="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="text-kelana">Kelana</span>
          </div>
          <p className="footer-text">&copy; 2026 Kelana. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
