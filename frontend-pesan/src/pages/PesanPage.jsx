import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import { ArrowLeft, ShieldCheck, CreditCard, Building2, Wallet, ChevronRight, CheckCircle2 } from 'lucide-react';
import './PesanPage.css';

const JALAN_URL = import.meta.env.VITE_JALAN_URL || 'http://localhost:5173';

const PAYMENT_METHODS = [
  { id: 'transfer', label: 'Transfer Bank', icon: Building2, desc: 'BCA, Mandiri, BNI, BRI' },
  { id: 'credit', label: 'Kartu Kredit', icon: CreditCard, desc: 'Visa, Mastercard' },
  { id: 'ewallet', label: 'E-Wallet', icon: Wallet, desc: 'GoPay, OVO, Dana' },
];

const PesanPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const hotelId = searchParams.get('hotelId') || 'HT001';
  const roomType = searchParams.get('room') || 'Standard Double';
  const price = parseInt(searchParams.get('price')) || 450000;
  const query = searchParams.get('query') || '';

  const [paymentMethod, setPaymentMethod] = useState('transfer');
  const [formData, setFormData] = useState({ name: '', email: '', phone: '' });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const nights = 2;
  const subtotal = price * nights;
  const tax = Math.round(subtotal * 0.11);
  const total = subtotal + tax;

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div className="pesan-page">
        <header className="pesan-navbar">
          <div className="pesan-navbar-inner">
            <div className="pesan-logo">
              <span className="text-singgah-brand">Singgah</span>
            </div>
          </div>
        </header>
        <div className="checkout-success fade-in-up">
          <div className="success-icon-wrapper">
            <CheckCircle2 size={56} />
          </div>
          <h1>Pembayaran Berhasil!</h1>
          <p className="text-muted">Terima kasih, pemesanan Anda telah dikonfirmasi.</p>
          <div className="success-summary">
            <div className="success-row">
              <span>Kamar</span>
              <strong>{roomType}</strong>
            </div>
            <div className="success-row">
              <span>Durasi</span>
              <strong>{nights} malam</strong>
            </div>
            <div className="success-row">
              <span>Total Dibayar</span>
              <strong className="text-sky">Rp {total.toLocaleString('id-ID')}</strong>
            </div>
          </div>
          <div className="success-actions">
            <Button
              variant="primary"
              theme="sky"
              onClick={() => window.location.href = JALAN_URL}
            >
              Kembali ke Kelana
            </Button>
            <Button
              variant="outline"
              theme="sky"
              onClick={() => window.location.href = `${JALAN_URL}/plan?q=${encodeURIComponent(query)}`}
            >
              Lihat Itinerary
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pesan-page">
      {/* Navbar */}
      <header className="pesan-navbar">
        <div className="pesan-navbar-inner">
          <button
            onClick={() => navigate(`/hotel/${hotelId}?query=${encodeURIComponent(query)}`)}
            className="pesan-back-link"
            style={{ background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <ArrowLeft size={18} />
            <span>Kembali</span>
          </button>
          <nav className="pesan-nav-tabs">
            <a href="#" className="pesan-nav-tab">Hotel</a>
            <a href="#" className="pesan-nav-tab">Pesawat</a>
            <a href="#" className="pesan-nav-tab">Aktivitas</a>
          </nav>
          <div className="pesan-logo">
            <span className="text-singgah-brand">Singgah</span>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="checkout-breadcrumb">
        <div className="breadcrumb-inner">
          <span className="text-light text-caption">Hotel</span>
          <ChevronRight size={12} className="text-light" />
          <span className="text-caption font-semibold">Checkout</span>
        </div>
      </div>

      <main className="checkout-main">
        <h1 className="checkout-page-title">Checkout</h1>

        <form onSubmit={handleSubmit} className="checkout-layout">
          {/* Left column */}
          <div className="checkout-left">
            {/* Guest data */}
            <section className="checkout-section">
              <h2 className="checkout-section-title">Data Pemesan</h2>
              <div className="form-group">
                <label htmlFor="guest-name" className="form-label">Nama Lengkap</label>
                <input
                  id="guest-name"
                  type="text"
                  className="form-input"
                  placeholder="Nizar Arfin"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="guest-email" className="form-label">Email</label>
                <input
                  id="guest-email"
                  type="email"
                  className="form-input"
                  placeholder="nizar@email.com"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="guest-phone" className="form-label">No. Telepon</label>
                <input
                  id="guest-phone"
                  type="tel"
                  className="form-input"
                  placeholder="+62 812 xxxx xxxx"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  required
                />
              </div>
            </section>

            {/* Payment method */}
            <section className="checkout-section">
              <h2 className="checkout-section-title">
                Metode Pembayaran
                <ShieldCheck size={16} className="text-sky" />
              </h2>
              <div className="payment-methods">
                {PAYMENT_METHODS.map((method) => (
                  <div
                    key={method.id}
                    className={`payment-method-card ${paymentMethod === method.id ? 'payment-method-selected' : ''}`}
                    onClick={() => setPaymentMethod(method.id)}
                    role="radio"
                    aria-checked={paymentMethod === method.id}
                    tabIndex={0}
                  >
                    <div className="payment-method-radio">
                      <div className={`radio-dot ${paymentMethod === method.id ? 'radio-dot-active' : ''}`}></div>
                    </div>
                    <method.icon size={20} className="payment-method-icon" />
                    <div className="payment-method-info">
                      <span className="payment-method-label">{method.label}</span>
                      <span className="payment-method-desc">{method.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Right column — Summary */}
          <div className="checkout-right">
            <div className="checkout-summary-card">
              <h2 className="checkout-section-title">Ringkasan Pesanan</h2>

              <div className="summary-hotel-name">Hotel Puri Saron Kuta</div>
              <div className="summary-room-type">{roomType}</div>

              <div className="summary-dates">
                <div className="summary-date-item">
                  <span className="summary-date-label">Check-in</span>
                  <span className="summary-date-value">15 Jan 2026</span>
                </div>
                <div className="summary-date-item">
                  <span className="summary-date-label">Check-out</span>
                  <span className="summary-date-value">17 Jan 2026</span>
                </div>
              </div>

              <div className="summary-detail-row">
                <span>{nights} malam × Rp {price.toLocaleString('id-ID')}</span>
                <span>Rp {subtotal.toLocaleString('id-ID')}</span>
              </div>

              <div className="summary-detail-row">
                <span>Pajak & Biaya Layanan</span>
                <span>Rp {tax.toLocaleString('id-ID')}</span>
              </div>

              <div className="summary-divider"></div>

              <div className="summary-total-row">
                <span>Total Pembayaran</span>
                <span className="summary-total-price">Rp {total.toLocaleString('id-ID')}</span>
              </div>

              <Button type="submit" variant="primary" theme="sky" size="lg" className="checkout-pay-btn">
                Bayar sekarang
              </Button>

              <p className="checkout-disclaimer">
                Dengan mengklik "Bayar sekarang", Anda menyetujui syarat dan ketentuan yang berlaku.
              </p>
            </div>
          </div>
        </form>
      </main>

      {/* Footer */}
      <footer className="pesan-footer">
        <p className="text-caption text-light">&copy; 2026 Singgah. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default PesanPage;
