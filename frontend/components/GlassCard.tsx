import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
  onClick?: () => void;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', hoverEffect = false, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className={`
        bg-white/10 
        backdrop-blur-lg 
        border border-white/20 
        shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] 
        rounded-2xl 
        p-6 
        text-white 
        transition-all 
        duration-300
        ${hoverEffect ? 'hover:bg-white/20 hover:scale-105 hover:shadow-xl cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};