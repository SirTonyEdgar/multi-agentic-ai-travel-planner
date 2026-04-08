import React from 'react';
import { Clock, MapPin, Star, ArrowRight } from 'lucide-react';
import './ItineraryTimeline.css';

const ItineraryTimeline = ({ days = [], onBooking }) => {
  if (!days.length) return null;

  return (
    <div className="itinerary-timeline">
      {days.map((day, dayIdx) => (
        <div key={dayIdx} className="timeline-day fade-in-up" style={{ animationDelay: `${dayIdx * 0.15}s` }}>
          <div className="timeline-day-header">
            <span className="timeline-day-badge">Hari {day.day}</span>
            {day.area && <span className="timeline-day-area"><MapPin size={12} /> {day.area}</span>}
          </div>
          
          <div className="timeline-activities">
            {day.activities.map((activity, actIdx) => (
              <div key={actIdx} className="timeline-activity">
                <div className="timeline-time-col">
                  <span className="timeline-time">{activity.time}</span>
                  <div className="timeline-dot"></div>
                  {actIdx < day.activities.length - 1 && <div className="timeline-line"></div>}
                </div>
                
                <div className="timeline-activity-card">
                  <div className="timeline-activity-info">
                    <h4 className="timeline-activity-name">{activity.name}</h4>
                    <p className="timeline-activity-desc">{activity.description}</p>
                    <div className="timeline-activity-meta">
                      {activity.duration && (
                        <span className="meta-item">
                          <Clock size={12} /> ~{activity.duration} jam
                        </span>
                      )}
                      {activity.rating && (
                        <span className="meta-item">
                          <Star size={12} /> {activity.rating}
                        </span>
                      )}
                      {activity.price && (
                        <span className="meta-item meta-price">
                          {activity.price}
                        </span>
                      )}
                    </div>
                  </div>
                  {activity.bookable && onBooking && (
                    <button 
                      className="timeline-booking-btn"
                      onClick={() => onBooking(activity)}
                    >
                      Booking <ArrowRight size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ItineraryTimeline;
