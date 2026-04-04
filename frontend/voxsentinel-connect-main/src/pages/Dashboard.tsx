import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Phone, ShieldCheck, AlertTriangle, BarChart3, Loader2 } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import AnimatedCounter from "@/components/AnimatedCounter";
import MiniSparkline from "@/components/MiniSparkline";
import PageTransition from "@/components/PageTransition";
import { useDashboardStats } from "@/hooks/useApi";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" as const } },
};

const statusColor = (status: string) => {
  switch (status) {
    case "Compliant": return "text-success bg-success/10";
    case "Flagged": 
    case "Non-Compliant": return "text-destructive bg-destructive/10";
    default: return "text-warning bg-warning/10";
  }
};

const SENTIMENT_COLORS = {
  positive: "#22c55e",
  neutral: "#6366f1",
  negative: "#ef4444",
};

const Dashboard = () => {
  const { data: stats, isLoading, isError, error, refetch } = useDashboardStats();

  // Loading state
  if (isLoading) {
    return (
      <PageTransition>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  // Use real data or empty defaults (no mock data)
  const displayStats = stats || {
    total_calls: 0,
    avg_compliance: 0,
    compliant_calls: 0,
    non_compliant_calls: 0,
    partial_calls: 0,
    sentiment_distribution: { positive: 0, neutral: 0, negative: 0 },
    calls_today: 0,
    calls_this_week: 0,
    recent_calls: [],
  };

  // Compute KPIs
  const kpis = [
    { 
      label: "Total Calls", 
      value: displayStats.total_calls, 
      prefix: "", 
      suffix: "", 
      icon: Phone, 
      trend: `+${displayStats.calls_today} today`, 
      up: true, 
      spark: [380, 420, 390, 510, 440, 390, displayStats.calls_today] 
    },
    { 
      label: "Compliance Rate", 
      value: displayStats.avg_compliance,  // Backend already returns as percentage
      prefix: "", 
      suffix: "%", 
      decimals: 1, 
      icon: ShieldCheck, 
      trend: displayStats.avg_compliance >= 90 ? "On target" : "Below target",  // Compare to 90% not 0.90
      up: displayStats.avg_compliance >= 90, 
      spark: [91, 93, 89, 95, 94, 97, displayStats.avg_compliance] 
    },
    { 
      label: "Flagged Calls", 
      value: displayStats.non_compliant_calls, 
      prefix: "", 
      suffix: "", 
      icon: AlertTriangle, 
      trend: displayStats.non_compliant_calls <= 50 ? "Within limits" : "High", 
      up: displayStats.non_compliant_calls <= 50, 
      spark: [52, 48, 45, 42, 40, 39, displayStats.non_compliant_calls] 
    },
    { 
      label: "This Week", 
      value: displayStats.calls_this_week, 
      prefix: "", 
      suffix: "", 
      icon: BarChart3, 
      trend: "7-day total", 
      up: true, 
      spark: [82, 84, 85, 86, 85, 87, displayStats.calls_this_week / 7] 
    },
  ];

  // Sentiment pie chart data
  const sentimentData = displayStats.sentiment_distribution ? [
    { name: "Positive", value: displayStats.sentiment_distribution.positive, color: SENTIMENT_COLORS.positive },
    { name: "Neutral", value: displayStats.sentiment_distribution.neutral, color: SENTIMENT_COLORS.neutral },
    { name: "Negative", value: displayStats.sentiment_distribution.negative, color: SENTIMENT_COLORS.negative },
  ] : [];

  // Mock chart data (would come from API trend endpoint in production)
  const chartData = [
    { name: "Mon", compliance: 91, calls: 420 },
    { name: "Tue", compliance: 93, calls: 380 },
    { name: "Wed", compliance: 89, calls: 510 },
    { name: "Thu", compliance: 95, calls: 440 },
    { name: "Fri", compliance: 94, calls: 390 },
    { name: "Sat", compliance: 97, calls: 210 },
    { name: "Sun", compliance: Math.round(displayStats.avg_compliance), calls: displayStats.calls_today },  // Already a percentage
  ];

  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Monitor call compliance in real-time</p>
          {isError && (
            <p className="mt-1 text-xs text-warning">
              ⚠️ Failed to fetch - {error?.message || "Backend may be offline"}
            </p>
          )}
        </div>

        {/* KPI Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {kpis.map((kpi) => (
            <motion.div
              key={kpi.label}
              variants={item}
              className="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-colors hover:bg-accent/50 active:scale-[0.98]"
            >
              <MiniSparkline data={kpi.spark} className="pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{kpi.label}</span>
                  <kpi.icon className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="mt-2 text-3xl font-bold text-foreground">
                  <AnimatedCounter
                    value={kpi.value}
                    prefix={kpi.prefix}
                    suffix={kpi.suffix}
                    decimals={kpi.decimals ?? 0}
                  />
                </div>
                <div className={`mt-1 flex items-center gap-1 text-xs ${kpi.up ? "text-success" : "text-destructive"}`}>
                  {kpi.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  <span>{kpi.trend}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Charts Row */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 lg:grid-cols-3"
        >
          {/* Compliance Trend Chart */}
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-5 lg:col-span-2">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Compliance Trend</h3>
              <p className="text-xs text-muted-foreground">Weekly overview</p>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="complianceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: "hsl(240, 4%, 46%)" }}
                  />
                  <YAxis
                    domain={[80, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: "hsl(240, 4%, 46%)" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="compliance"
                    stroke="hsl(239, 84%, 67%)"
                    strokeWidth={2}
                    fill="url(#complianceGrad)"
                    animationDuration={1500}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Sentiment Distribution Pie */}
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-5">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Sentiment Distribution</h3>
              <p className="text-xs text-muted-foreground">Call sentiment breakdown</p>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4">
              {sentimentData.map((item) => (
                <div key={item.name} className="flex items-center gap-1.5 text-xs">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-muted-foreground">{item.name}</span>
                  <span className="font-medium text-foreground">{item.value}%</span>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* Recent Calls Table */}
        <motion.div variants={container} initial="hidden" animate="show">
          <motion.div variants={item} className="overflow-hidden rounded-xl border border-border bg-card">
            <div className="px-5 py-4 border-b border-border">
              <h3 className="text-sm font-medium text-foreground">Recent Calls</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-accent/30">
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">ID</th>
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Language</th>
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Date</th>
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Sentiment</th>
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Score</th>
                    <th className="px-4 py-2.5 text-left text-xs font-medium text-muted-foreground">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {displayStats.recent_calls && displayStats.recent_calls.length > 0 ? (
                    displayStats.recent_calls.slice(0, 5).map((call, i) => (
                      <motion.tr
                        key={call.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 + i * 0.05, duration: 0.3 }}
                        className="border-b border-border/50 transition-colors hover:bg-accent/30 last:border-0"
                      >
                        <td className="px-4 py-2.5 text-sm font-mono text-muted-foreground">{call.id.slice(0, 8)}</td>
                        <td className="px-4 py-2.5 text-sm text-foreground uppercase">{call.language}</td>
                        <td className="px-4 py-2.5 text-sm tabular-nums text-muted-foreground">
                          {new Date(call.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-2.5">
                          <span className={`rounded-md px-2 py-0.5 text-xs font-medium ${
                            call.sentiment === 'Positive' ? 'bg-success/10 text-success' :
                            call.sentiment === 'Negative' ? 'bg-destructive/10 text-destructive' :
                            'bg-accent text-foreground'
                          }`}>
                            {call.sentiment}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-sm font-semibold tabular-nums text-foreground">
                          {Math.round(call.compliance_score * 100)}%
                        </td>
                        <td className="px-4 py-2.5">
                          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(call.adherence_status)}`}>
                            {call.adherence_status}
                          </span>
                        </td>
                      </motion.tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                        No calls analyzed yet. Go to "Analyze Call" to analyze your first call.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </PageTransition>
  );
};

export default Dashboard;
