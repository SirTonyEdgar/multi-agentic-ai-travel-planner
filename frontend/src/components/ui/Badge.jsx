import React from 'react';
import './Badge.css';

const Badge = ({ children, variant = 'neutral', icon: Icon, className = '' }) => {
  return (
    <span className={`badge badge-${variant} ${className}`}>
      {Icon && <Icon size={14} className="badge-icon" />}
      {children}
    </span>
  );
};

export default Badge;
