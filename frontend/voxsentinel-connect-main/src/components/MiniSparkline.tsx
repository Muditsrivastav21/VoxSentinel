import { motion } from "framer-motion";

interface MiniSparklineProps {
  data: number[];
  color?: string;
  className?: string;
}

const MiniSparkline = ({ data, color = "hsl(var(--primary))", className = "" }: MiniSparklineProps) => {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const h = 32;
  const w = 80;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * (h - 4) - 2;
    return `${x},${y}`;
  });
  const linePath = `M${points.join(" L")}`;
  const areaPath = `${linePath} L${w},${h} L0,${h} Z`;

  return (
    <motion.svg
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.25 }}
      transition={{ duration: 1, delay: 0.5 }}
      viewBox={`0 0 ${w} ${h}`}
      className={`absolute bottom-0 right-0 ${className}`}
      style={{ width: 80, height: 32 }}
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient id={`spark-${data.join("")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.4} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#spark-${data.join("")})`} />
      <path d={linePath} fill="none" stroke={color} strokeWidth={1.5} />
    </motion.svg>
  );
};

export default MiniSparkline;
