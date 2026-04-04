const VoxLogo = ({ className = "h-8 w-8" }: { className?: string }) => (
  <svg viewBox="0 0 40 40" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
    <path
      d="M8 8L20 32L26 20"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-primary"
    />
    <rect x="29" y="12" width="2.5" height="16" rx="1.25" className="fill-primary" />
    <rect x="34" y="16" width="2.5" height="8" rx="1.25" className="fill-primary opacity-60" />
  </svg>
);

export default VoxLogo;
