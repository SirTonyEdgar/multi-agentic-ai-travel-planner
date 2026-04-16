import React from 'react';
import './Button.css';

const Button = ({ children, variant = 'primary', theme = 'warm', size = '', icon: Icon, className = '', ...props }) => {
  return (
    <button className={`btn btn-${variant} btn-theme-${theme} ${size ? `btn-${size}` : ''} ${className}`} {...props}>
      {Icon && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
      {children}
    </button>
  );
};

export default Button;
