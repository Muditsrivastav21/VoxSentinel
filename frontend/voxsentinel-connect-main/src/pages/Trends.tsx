import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Calendar, BarChart3, Loader2 } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, LineChart, Line } from "recharts";
import PageTransition from "@/components/PageTransition";
import { useTrends } from "@/hooks/useApi";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

const periodOptions = [
  { value: 7, label: '7 Days' },
  { value: 14, label: '14 Days' },
  { value: 30, label: '30 Days' },
] as const;

const Trends = () => {
  const [days, setDays] = useState(7);
  const { data, isLoading, isError, error } = useTrends(days);

  if (isLoading) {
    return (
      <PageTransition>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-muted-foreground">Loading trends...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  const trends = data?.trends || [];
  const totalCalls = data?.total_calls || 0;

  // Calculate averages
  const avgCompliance = trends.length > 0 
    ? trends.reduce((acc, t) => acc + t.avg_compliance, 0) / trends.length 
    : 0;
  
  const totalPositive = trends.reduce((acc, t) => acc + t.positive_sentiment, 0);
  const totalNegative = trends.reduce((acc, t) => acc + t.negative_sentiment, 0);

  // Calculate trend direction
  const recentAvg = trends.slice(-3).reduce((acc, t) => acc + t.avg_compliance, 0) / Math.min(3, trends.length);
  const olderAvg = trends.slice(0, 3).reduce((acc, t) => acc + t.avg_compliance, 0) / Math.min(3, trends.length);
  const isUpward = recentAvg >= olderAvg;

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-primary" />
              Compliance Trends
            </h1>
            <p className="text-sm text-muted-foreground">
              Track performance over time
            </p>
            {isError && (
              <p className="mt-1 text-xs text-warning">
                ⚠️ {error?.message || "Failed to load trends"}
              </p>
            )}
          </div>

          {/* Period Selector */}
          <div className="flex gap-2">
            {periodOptions.map((p) => (
              <button
                key={p.value}
                onClick={() => setDays(p.value)}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  days === p.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-accent text-foreground hover:bg-accent/80'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 sm:grid-cols-4"
        >
          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              Total Calls
            </div>
            <div className="mt-2 text-3xl font-bold text-foreground">
              {totalCalls}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Last {days} days</p>
          </motion.div>

          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              {isUpward ? (
                <TrendingUp className="h-4 w-4 text-success" />
              ) : (
                <TrendingDown className="h-4 w-4 text-destructive" />
              )}
              Avg Compliance
            </div>
            <div className="mt-2 text-3xl font-bold text-foreground">
              {avgCompliance.toFixed(1)}%
            </div>
            <p className={`text-xs mt-1 ${isUpward ? 'text-success' : 'text-destructive'}`}>
              {isUpward ? '↑ Improving' : '↓ Declining'}
            </p>
          </motion.div>

          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-success" />
              Positive Sentiment
            </div>
            <div className="mt-2 text-3xl font-bold text-success">
              {totalPositive}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalCalls > 0 ? ((totalPositive / totalCalls) * 100).toFixed(1) : 0}% of calls
            </p>
          </motion.div>

          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-destructive" />
              Negative Sentiment
            </div>
            <div className="mt-2 text-3xl font-bold text-destructive">
              {totalNegative}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalCalls > 0 ? ((totalNegative / totalCalls) * 100).toFixed(1) : 0}% of calls
            </p>
          </motion.div>
        </motion.div>

        {/* Charts */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 gap-4 lg:grid-cols-2"
        >
          {/* Compliance Trend Chart */}
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-5">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Compliance Score Trend</h3>
              <p className="text-xs text-muted-foreground">Daily average compliance</p>
            </div>
            <div className="h-64">
              {trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trends}>
                    <defs>
                      <linearGradient id="complianceGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="hsl(239, 84%, 67%)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="date"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                      tickFormatter={(val) => val.slice(5)}
                    />
                    <YAxis
                      domain={[0, 100]}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Compliance']}
                    />
                    <Area
                      type="monotone"
                      dataKey="avg_compliance"
                      stroke="hsl(239, 84%, 67%)"
                      strokeWidth={2}
                      fill="url(#complianceGrad)"
                      animationDuration={1500}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No data available
                </div>
              )}
            </div>
          </motion.div>

          {/* Daily Calls Chart */}
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-5">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Daily Call Volume</h3>
              <p className="text-xs text-muted-foreground">Calls processed per day</p>
            </div>
            <div className="h-64">
              {trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trends}>
                    <XAxis
                      dataKey="date"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                      tickFormatter={(val) => val.slice(5)}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Bar 
                      dataKey="total_calls" 
                      fill="hsl(239, 84%, 67%)" 
                      radius={[4, 4, 0, 0]}
                      animationDuration={1500}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No data available
                </div>
              )}
            </div>
          </motion.div>

          {/* Sentiment Trend */}
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-5 lg:col-span-2">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-foreground">Sentiment Over Time</h3>
              <p className="text-xs text-muted-foreground">Positive vs Negative sentiment trend</p>
            </div>
            <div className="h-64">
              {trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends}>
                    <XAxis
                      dataKey="date"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                      tickFormatter={(val) => val.slice(5)}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 10, fill: "hsl(240, 4%, 46%)" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="positive_sentiment" 
                      stroke="#22c55e" 
                      strokeWidth={2}
                      dot={false}
                      name="Positive"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="negative_sentiment" 
                      stroke="#ef4444" 
                      strokeWidth={2}
                      dot={false}
                      name="Negative"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  No data available
                </div>
              )}
            </div>
            <div className="flex justify-center gap-6 mt-2">
              <div className="flex items-center gap-2 text-xs">
                <div className="h-2 w-2 rounded-full bg-success" />
                <span className="text-muted-foreground">Positive</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="h-2 w-2 rounded-full bg-destructive" />
                <span className="text-muted-foreground">Negative</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </PageTransition>
  );
};

export default Trends;
