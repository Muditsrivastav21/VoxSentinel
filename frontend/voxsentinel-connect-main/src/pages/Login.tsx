import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, YAxis } from "recharts";
import VoxLogo from "@/components/VoxLogo";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import ThemeToggle from "@/components/ThemeToggle";

const complianceData = [
  { day: "M", value: 88 },
  { day: "T", value: 91 },
  { day: "W", value: 85 },
  { day: "T", value: 93 },
  { day: "F", value: 90 },
  { day: "S", value: 95 },
  { day: "S", value: 94.7 },
];

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1200));
    if (email === "admin@gmail.com" && password === "admin@123") {
      toast.success("Welcome back!");
      navigate("/dashboard");
    } else {
      toast.error("Invalid credentials");
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[hsl(240,10%,4%)]">
      {/* ── Dark animated backdrop (full background) ── */}
      <div className="absolute inset-0">
        {/* Gradient base */}
        <div className="absolute inset-0 bg-gradient-to-br from-[hsl(240,10%,6%)] via-[hsl(240,10%,4%)] to-[hsl(258,30%,8%)]" />

        {/* Ambient orbs */}
        <motion.div
          animate={{ x: [0, 40, -30, 0], y: [0, -50, 30, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[20%] left-[25%] h-[500px] w-[500px] rounded-full bg-[hsl(239,84%,67%,0.07)] blur-[120px]"
        />
        <motion.div
          animate={{ x: [0, -35, 45, 0], y: [0, 40, -35, 0] }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[15%] right-[20%] h-[400px] w-[400px] rounded-full bg-[hsl(258,90%,66%,0.06)] blur-[100px]"
        />

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(hsl(0,0%,100%) 1px, transparent 1px), linear-gradient(90deg, hsl(0,0%,100%) 1px, transparent 1px)`,
            backgroundSize: "60px 60px",
          }}
        />

        {/* Breathing logo watermark */}
        <motion.div
          animate={{ scale: [1, 1.05, 1], opacity: [0.02, 0.05, 0.02] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <VoxLogo className="h-[500px] w-[500px] text-[hsl(239,84%,67%)]" />
        </motion.div>
      </div>

      {/* ── Theme toggle (top right) ── */}
      <div className="absolute top-4 right-4 z-30">
        <ThemeToggle />
      </div>

      {/* ── Floating compliance card (background decoration, offset right) ── */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease: "easeOut" }}
        className="absolute right-[8%] z-10 hidden w-[300px] rounded-xl border border-[hsl(0,0%,100%,0.08)] bg-[hsl(240,6%,10%,0.85)] p-5 shadow-2xl backdrop-blur-lg lg:block"
      >
        <div className="mb-1 text-sm font-medium text-[hsl(0,0%,98%)]">Compliance Score</div>
        <div className="mb-0.5 text-3xl font-bold tabular-nums text-[hsl(239,84%,67%)]">94.7%</div>
        <div className="mb-4 text-xs text-[hsl(240,5%,55%)]">+2.3% from last month</div>
        <div className="h-28 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={complianceData}>
              <defs>
                <linearGradient id="loginCompGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <YAxis domain={[80, 100]} hide />
              <Area type="monotone" dataKey="value" stroke="hsl(239, 84%, 67%)" strokeWidth={2} fill="url(#loginCompGrad)" animationDuration={2000} animationBegin={800} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-3 space-y-2">
          {[
            { label: "Greeting", value: 85 },
            { label: "Disclosure", value: 92 },
            { label: "Verification", value: 78 },
            { label: "Closing", value: 96 },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <span className="w-20 text-xs text-[hsl(240,5%,55%)]">{item.label}</span>
              <div className="h-1.5 flex-1 rounded-full bg-[hsl(240,4%,16%)] overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.value}%` }}
                  transition={{ delay: 1.2 + i * 0.15, duration: 0.8, ease: "easeOut" }}
                  className="h-full rounded-full bg-[hsl(239,84%,67%)]"
                />
              </div>
              <span className="w-8 text-right text-xs tabular-nums text-[hsl(240,5%,55%)]">{item.value}%</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Login card (centered, light themed) ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative z-20 w-full max-w-md rounded-2xl border border-border bg-background p-8 shadow-2xl lg:ml-[-15%]"
      >
        <div className="space-y-8">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <VoxLogo className="h-9 w-9" />
              <span className="text-xl font-semibold tracking-tight text-foreground">VoxSentinel</span>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">Welcome back</h1>
            <p className="text-sm text-muted-foreground">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="focus-visible:ring-2 focus-visible:ring-primary"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="focus-visible:ring-2 focus-visible:ring-primary"
              />
            </div>
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 active:scale-[0.98] transition-all"
            >
              {loading ? (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  <Loader2 className="h-4 w-4 animate-spin" />
                </motion.div>
              ) : (
                "Sign in"
              )}
            </Button>
          </form>

          <p className="text-center text-xs text-muted-foreground">
            For testing, use <span className="font-medium text-foreground/70">admin@gmail.com</span> / <span className="font-medium text-foreground/70">admin@123</span>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
