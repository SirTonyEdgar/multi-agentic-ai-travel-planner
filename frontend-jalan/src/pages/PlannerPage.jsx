import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ChatBubble from '../components/ui/ChatBubble';
import AgentProgress from '../components/ui/AgentProgress';
import ItineraryTimeline from '../components/ui/ItineraryTimeline';
import { Send, ArrowLeft, RotateCcw, Sparkles, MessageSquare, Calendar } from 'lucide-react';
import './PlannerPage.css';

const PESAN_URL = 'http://localhost:5174';

// Parse AI response text into structured itinerary
function parseItinerary(text) {
  if (!text) return [];
  const days = [];
  // Simple heuristic parser — looks for day patterns and activities
  const dayRegex = /(?:Hari|Day)\s*(\d+)/gi;
  const sections = text.split(dayRegex);

  for (let i = 1; i < sections.length; i += 2) {
    const dayNum = parseInt(sections[i]);
    const content = sections[i + 1] || '';
    const activities = [];

    // Extract activities from content
    const lines = content.split('\n').filter(l => l.trim());
    let timeCounter = 8; // Start at 8 AM

    for (const line of lines) {
      const cleaned = line.replace(/^[-•*]\s*/, '').trim();
      if (!cleaned || cleaned.length < 5) continue;

      // Try to extract time
      const timeMatch = cleaned.match(/(\d{1,2}[:.]\d{2})/);
      const time = timeMatch ? timeMatch[1].replace('.', ':') : `${String(timeCounter).padStart(2, '0')}:00`;
      if (!timeMatch) timeCounter += 2;

      // Try to extract price
      const priceMatch = cleaned.match(/Rp\s*([\d.,]+)/i);
      const price = priceMatch ? `Rp ${priceMatch[1]}` : null;

      // Try to extract rating
      const ratingMatch = cleaned.match(/Rating:\s*([\d.]+)/i);
      const rating = ratingMatch ? parseFloat(ratingMatch[1]) : null;

      // Remove time prefix and clean name
      let name = cleaned.replace(/^\d{1,2}[:.]\d{2}\s*[-–]\s*/, '').trim();
      // Take only first part as name (before | or long description)
      const nameParts = name.split(/\s*[|]\s*/);
      name = nameParts[0].substring(0, 60);

      activities.push({
        time,
        name,
        description: nameParts.length > 1 ? nameParts.slice(1).join(' · ') : '',
        price,
        rating,
        duration: null,
        bookable: !!priceMatch,
      });
    }

    if (activities.length > 0) {
      days.push({ day: dayNum, activities, area: '' });
    }
  }

  return days;
}

// Fallback mock data based on actual activities.json
const MOCK_RESPONSE = {
  bali: `Berikut rekomendasi perjalanan ke Bali:

**Hari 1 - Area Kuta & Seminyak**
09:00 - Pantai Kuta | Pantai ikonik Bali yang terkenal dengan ombak dan sunset-nya | Rating: 4.3 | Gratis
12:00 - Warung Babi Guling Ibu Oka | Warung babi guling legendaris yang terkenal di Ubud | Rating: 4.6 | Rp 65,000
15:00 - Waterbom Bali | Taman air terbesar di Asia dengan berbagai wahana seru | Rating: 4.8 | Rp 395,000

**Hari 2 - Area Ubud**
08:00 - Tegalalang Rice Terrace | Sawah berteras yang indah, cocok untuk foto dan trekking | Rating: 4.5 | Rp 15,000
11:00 - Monkey Forest Ubud | Hutan sakral dengan ratusan monyet ekor panjang dan pura kuno | Rating: 4.6 | Rp 80,000
14:00 - Jimbaran Seafood | Makan malam seafood segar di tepi pantai Jimbaran | Rating: 4.5 | Rp 150,000

**Hari 3 - Area Tabanan**
09:00 - Tanah Lot | Pura di atas batu karang di tepi laut, ikonik saat sunset | Rating: 4.7 | Rp 60,000
12:00 - Masjid Agung Bali | Masjid terbesar di Bali, cocok untuk salat dan wisata religi | Rating: 4.4 | Gratis

**Estimasi Total Biaya Aktivitas: Rp 765,000**`,

  yogyakarta: `Berikut rekomendasi perjalanan ke Yogyakarta:

**Hari 1 - Candi & Sejarah**
06:00 - Candi Borobudur | Candi Buddha terbesar di dunia, Warisan Dunia UNESCO | Rating: 4.8 | Rp 50,000
12:00 - Malioboro Street Food | Jajanan kaki lima khas Jogja sepanjang Jalan Malioboro | Rating: 4.4 | Rp 25,000

**Hari 2 - Budaya & Religi**
08:00 - Candi Prambanan | Kompleks candi Hindu terbesar di Indonesia | Rating: 4.7 | Rp 50,000
14:00 - Masjid Gedhe Kauman Yogyakarta | Masjid Agung Kesultanan Yogyakarta, bersejarah dan dekat Kraton | Rating: 4.6 | Gratis

**Estimasi Total Biaya Aktivitas: Rp 125,000**`,

  lombok: `Berikut rekomendasi perjalanan ke Lombok:

**Hari 1 - Gili Islands**
08:00 - Gili Trawangan Snorkeling | Snorkeling di perairan jernih Gili Trawangan, full equipment tersedia | Rating: 4.8 | Rp 150,000

**Hari 2 - Mataram**
09:00 - Masjid Islamic Center Lombok | Masjid ikonik Lombok dengan kubah besar, pemandangan indah | Rating: 4.7 | Gratis

**Estimasi Total Biaya Aktivitas: Rp 150,000**`,
};

function getMockResponse(query) {
  const q = query.toLowerCase();
  if (q.includes('bali') || q.includes('kuta') || q.includes('ubud')) return MOCK_RESPONSE.bali;
  if (q.includes('yogya') || q.includes('jogja') || q.includes('borobudur')) return MOCK_RESPONSE.yogyakarta;
  if (q.includes('lombok') || q.includes('gili')) return MOCK_RESPONSE.lombok;
  // Default
  return MOCK_RESPONSE.bali;
}

const AGENT_SEQUENCE = ['preferensi', 'destinasi', 'itinerary', 'ringkasan'];

const PlannerPage = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const navigate = useNavigate();
  const [sessionId] = useState(() => crypto.randomUUID());

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [itineraryDays, setItineraryDays] = useState([]);
  const [activeTab, setActiveTab] = useState('chat'); // for mobile toggle

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Initial query from Landing Page
  const hasSentInitialQuery = useRef(false);
  useEffect(() => {
    if (initialQuery && messages.length === 0 && !hasSentInitialQuery.current) {
      hasSentInitialQuery.current = true;
      sendMessage(initialQuery);
    }
  }, []);

  const simulateAgentProgress = () => {
    return new Promise((resolve) => {
      let idx = 0;
      const interval = setInterval(() => {
        if (idx < AGENT_SEQUENCE.length) {
          setActiveAgent(AGENT_SEQUENCE[idx]);
          if (idx > 0) {
            setCompletedAgents(prev => [...prev, AGENT_SEQUENCE[idx - 1]]);
          }
          idx++;
        } else {
          setCompletedAgents(prev => [...prev, AGENT_SEQUENCE[AGENT_SEQUENCE.length - 1]]);
          setActiveAgent(null);
          clearInterval(interval);
          resolve();
        }
      }, 800);
    });
  };

  const sendMessage = async (text) => {
    const userMsg = text.trim();
    if (!userMsg) return;

    // Add user message
    const timestamp = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
    setMessages(prev => [...prev, { text: userMsg, sender: 'user', timestamp }]);
    setInput('');
    setLoading(true);
    setCompletedAgents([]);
    setActiveAgent(null);

    // Simulate agent progress
    const progressPromise = simulateAgentProgress();

    try {
      // Try real API first
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await fetch(`${API_URL}/api/chat?query=${encodeURIComponent(userMsg)}&session_id=${sessionId}`);

      if (response.ok) {
        const data = await response.json();
        await progressPromise;

        const aiText = data.response || data.itinerary || JSON.stringify(data);
        const aiTimestamp = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
        setMessages(prev => [...prev, { text: aiText, sender: 'ai', timestamp: aiTimestamp }]);

        // Parse itinerary
        const parsed = parseItinerary(aiText);
        if (parsed.length > 0) {
          setItineraryDays(parsed);
        }
      } else {
        throw new Error('API not available');
      }
    } catch (error) {
      console.log('Using fallback mock data:', error.message);
      await progressPromise;

      // Use fallback mock data from activities.json
      const mockText = getMockResponse(userMsg);
      const aiTimestamp = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
      setMessages(prev => [...prev, { text: mockText, sender: 'ai', timestamp: aiTimestamp }]);

      const parsed = parseItinerary(mockText);
      if (parsed.length > 0) {
        setItineraryDays(parsed);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleBooking = (activity) => {
    // Redirect ke website Singgah (external)
    window.open(
      `${PESAN_URL}/hotel/HT001?name=${encodeURIComponent(activity.name)}&query=${encodeURIComponent(initialQuery)}`,
      '_blank'
    );
  };

  const handleRegenerate = () => {
    if (messages.length > 0) {
      const lastUserMsg = [...messages].reverse().find(m => m.sender === 'user');
      if (lastUserMsg) {
        sendMessage(lastUserMsg.text);
      }
    }
  };

  return (
    <div className="planner-page">
      {/* Navbar */}
      <header className="planner-navbar">
        <Link to="/" className="planner-logo">
          <ArrowLeft size={18} />
          <span className="text-kelana">Kelana</span>
        </Link>
        <div className="planner-nav-center">
          <span className="planner-query-label">{initialQuery || 'Travel Planner'}</span>
        </div>
        <div className="planner-nav-actions">
          <Button variant="ghost" theme="warm" size="sm" icon={RotateCcw} onClick={handleRegenerate}>
            Regenerate
          </Button>
        </div>
      </header>

      {/* Mobile tab toggle */}
      <div className="mobile-tab-bar">
        <button
          className={`mobile-tab ${activeTab === 'chat' ? 'mobile-tab-active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={16} /> Percakapan
        </button>
        <button
          className={`mobile-tab ${activeTab === 'itinerary' ? 'mobile-tab-active' : ''}`}
          onClick={() => setActiveTab('itinerary')}
        >
          <Calendar size={16} /> Itinerary
        </button>
      </div>

      {/* Main content */}
      <main className="planner-main">
        {/* Left: Chat */}
        <div className={`planner-chat-panel ${activeTab === 'chat' ? 'panel-active' : ''}`}>
          {/* Agent Progress */}
          <div className="planner-agent-section">
            <AgentProgress activeAgent={activeAgent} completedAgents={completedAgents} />
          </div>

          {/* Chat messages */}
          <div className="planner-chat-messages" id="chat-messages">
            {messages.length === 0 && !loading && (
              <div className="chat-empty-state">
                <Sparkles size={40} className="text-warm" />
                <h3>Mulai rencanakan perjalananmu</h3>
                <p className="text-muted text-sm">Ketik tujuan wisatamu dan biarkan AI agen kami meracikkan itinerary terbaik untukmu.</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <ChatBubble
                key={idx}
                message={msg.text}
                sender={msg.sender}
                timestamp={msg.timestamp}
              />
            ))}

            {loading && <ChatBubble isTyping />}

            <div ref={chatEndRef} />
          </div>

          {/* Chat input */}
          <form onSubmit={handleSubmit} className="planner-chat-input" id="chat-input-form">
            <div className="chat-input-wrapper">
              <input
                ref={inputRef}
                type="text"
                id="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Tambahkan instruksi atau revisi..."
                disabled={loading}
                autoComplete="off"
              />
              <button
                type="submit"
                className="chat-send-btn"
                disabled={!input.trim() || loading}
                aria-label="Kirim pesan"
              >
                <Send size={18} />
              </button>
            </div>
          </form>
        </div>

        {/* Right: Itinerary */}
        <div className={`planner-itinerary-panel ${activeTab === 'itinerary' ? 'panel-active' : ''}`}>
          <div className="itinerary-panel-header">
            <Badge variant="warm" icon={Calendar}>Itinerary</Badge>
            <h2 className="itinerary-panel-title">
              {initialQuery
                ? `Itinerary — ${initialQuery.length > 30 ? initialQuery.substring(0, 30) + '...' : initialQuery}`
                : 'Itinerary Perjalanan'
              }
            </h2>
          </div>

          <div className="itinerary-panel-content">
            {itineraryDays.length > 0 ? (
              <ItineraryTimeline days={itineraryDays} onBooking={handleBooking} />
            ) : (
              <div className="itinerary-empty-state">
                <Calendar size={40} className="text-light" />
                <p className="text-muted text-sm">Itinerary akan muncul di sini setelah AI selesai menganalisis.</p>
              </div>
            )}
          </div>

          {itineraryDays.length > 0 && (
            <div className="itinerary-panel-footer">
              <div className="budget-summary">
                <span className="budget-label">Estimasi Budget</span>
                <span className="budget-amount">
                  {(() => {
                    let total = 0;
                    itineraryDays.forEach(day =>
                      day.activities.forEach(a => {
                        if (a.price) {
                          const num = parseInt(a.price.replace(/[^\d]/g, ''));
                          if (!isNaN(num)) total += num;
                        }
                      })
                    );
                    return `Rp ${total.toLocaleString('id-ID')}`;
                  })()}
                </span>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PlannerPage;
