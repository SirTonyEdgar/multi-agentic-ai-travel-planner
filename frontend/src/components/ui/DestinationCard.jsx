import React from 'react';
import { MapPin, Star } from 'lucide-react';
import './DestinationCard.css';

const DestinationCard = ({ name, image, activities, rating, onClick, className = '' }) => {
  return (
    <div className={`destination-card ${className}`} onClick={onClick} role="button" tabIndex={0}>
      <div className="destination-card-img-wrapper">
        <img src={image} alt={name} className="destination-card-img" loading="lazy" />
        <div className="destination-card-overlay"></div>
        <div className="destination-card-badge">
          <MapPin size={12} />
          <span>{name}</span>
        </div>
      </div>
      <div className="destination-card-body">
        <h3 className="destination-card-title">{name}</h3>
        <div className="destination-card-meta">
          {activities && <span className="destination-card-count">{activities} aktivitas</span>}
          {rating && (
            <span className="destination-card-rating">
              <Star size={12} fill="currentColor" /> {rating}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default DestinationCard;
