import { motion } from 'framer-motion';

interface ShieldLogoProps {
  size?: number;
  animate?: boolean;
  className?: string;
}

export const ShieldLogo: React.FC<ShieldLogoProps> = ({
  size = 64,
  animate = false,
  className = ''
}) => {
  return (
    <motion.div
      className={`inline-block ${className}`}
      initial={animate ? { scale: 0.8, opacity: 0 } : {}}
      animate={animate ? { scale: 1, opacity: 1 } : {}}
      transition={{ duration: 0.5 }}
    >
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 256 256"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        animate={animate ? {
          filter: [
            'drop-shadow(0 0 10px rgba(139, 0, 0, 0.5))',
            'drop-shadow(0 0 20px rgba(139, 0, 0, 0.8))',
            'drop-shadow(0 0 10px rgba(139, 0, 0, 0.5))',
          ],
        } : {}}
        transition={animate ? {
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        } : {}}
      >
        {/* Gradients */}
        <defs>
          <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8B0000" stopOpacity="1" />
            <stop offset="100%" stopColor="#DC143C" stopOpacity="1" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Main shield shape */}
        <motion.path
          d="M128 20 L40 60 L40 120 C40 180 80 220 128 236 C176 220 216 180 216 120 L216 60 Z"
          fill="url(#shieldGradient)"
          stroke="#B22222"
          strokeWidth="4"
          filter="url(#glow)"
          initial={animate ? { pathLength: 0 } : {}}
          animate={animate ? { pathLength: 1 } : {}}
          transition={animate ? { duration: 1.5, ease: 'easeInOut' } : {}}
        />

        {/* Inner circuit pattern */}
        <g opacity="0.8">
          {/* Central chip/lock icon */}
          <rect x="108" y="90" width="40" height="40" rx="4" fill="#fff" opacity="0.9"/>
          <circle cx="128" cy="110" r="8" fill="#8B0000"/>

          {/* Circuit lines */}
          <line x1="128" y1="80" x2="128" y2="90" stroke="#fff" strokeWidth="2"/>
          <line x1="108" y1="110" x2="90" y2="110" stroke="#fff" strokeWidth="2"/>
          <line x1="148" y1="110" x2="166" y2="110" stroke="#fff" strokeWidth="2"/>
          <line x1="128" y1="130" x2="128" y2="150" stroke="#fff" strokeWidth="2"/>

          {/* Circuit nodes */}
          <motion.circle
            cx="128" cy="80" r="3" fill="#fff"
            animate={animate ? { opacity: [1, 0.5, 1] } : {}}
            transition={animate ? { duration: 1.5, repeat: Infinity } : {}}
          />
          <motion.circle
            cx="90" cy="110" r="3" fill="#fff"
            animate={animate ? { opacity: [1, 0.5, 1] } : {}}
            transition={animate ? { duration: 1.5, repeat: Infinity, delay: 0.3 } : {}}
          />
          <motion.circle
            cx="166" cy="110" r="3" fill="#fff"
            animate={animate ? { opacity: [1, 0.5, 1] } : {}}
            transition={animate ? { duration: 1.5, repeat: Infinity, delay: 0.6 } : {}}
          />
          <motion.circle
            cx="128" cy="150" r="3" fill="#fff"
            animate={animate ? { opacity: [1, 0.5, 1] } : {}}
            transition={animate ? { duration: 1.5, repeat: Infinity, delay: 0.9 } : {}}
          />

          {/* Lock keyhole */}
          <circle cx="128" cy="115" r="4" fill="#8B0000"/>
          <rect x="126" y="115" width="4" height="8" fill="#8B0000"/>
        </g>

        {/* Subtle geometric accents */}
        <polygon points="128,40 120,50 136,50" fill="#fff" opacity="0.3"/>
        <polygon points="128,200 120,190 136,190" fill="#fff" opacity="0.3"/>
      </motion.svg>
    </motion.div>
  );
};
