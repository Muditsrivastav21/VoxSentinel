import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}

const AnimatedCounter = ({ value, duration = 1.5, prefix = "", suffix = "", decimals = 0 }: AnimatedCounterProps) => {
  const spring = useSpring(0, { duration: duration * 1000, bounce: 0 });
  const display = useTransform(spring, (v) =>
    `${prefix}${v.toFixed(decimals)}${suffix}`
  );
  const [displayValue, setDisplayValue] = useState(`${prefix}0${suffix}`);

  useEffect(() => {
    spring.set(value);
    const unsub = display.on("change", (v) => setDisplayValue(v));
    return unsub;
  }, [value, spring, display]);

  return (
    <motion.span className="tabular-nums">
      {displayValue}
    </motion.span>
  );
};

export default AnimatedCounter;
