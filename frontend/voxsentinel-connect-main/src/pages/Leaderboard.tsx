import { useState } from "react";
import { motion } from "framer-motion";
import { Trophy, Medal, TrendingUp, Users, Loader2 } from "lucide-react";
import PageTransition from "@/components/PageTransition";
import { useLeaderboard } from "@/hooks/useApi";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

const getRankBadge = (rank: number) => {
  if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
  if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
  if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />;
  return <span className="text-sm font-mono text-muted-foreground">#{rank}</span>;
};

const periods = [
  { value: 'day', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'all', label: 'All Time' },
] as const;

const Leaderboard = () => {
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'all'>('week');
  const { data, isLoading, isError, error } = useLeaderboard(period);

  if (isLoading) {
    return (
      <PageTransition>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-muted-foreground">Loading leaderboard...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  const leaderboard = data?.leaderboard || [];

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground flex items-center gap-2">
              <Trophy className="h-6 w-6 text-yellow-500" />
              Performance Leaderboard
            </h1>
            <p className="text-sm text-muted-foreground">
              Track compliance performance by category
            </p>
            {isError && (
              <p className="mt-1 text-xs text-warning">
                ⚠️ {error?.message || "Failed to load leaderboard"}
              </p>
            )}
          </div>

          {/* Period Selector */}
          <div className="flex gap-2">
            {periods.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  period === p.value
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
          className="grid grid-cols-1 gap-4 sm:grid-cols-3"
        >
          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Users className="h-4 w-4" />
              Total Categories
            </div>
            <div className="mt-2 text-3xl font-bold text-foreground">
              {leaderboard.length}
            </div>
          </motion.div>

          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              Top Score
            </div>
            <div className="mt-2 text-3xl font-bold text-foreground">
              {leaderboard[0]?.avg_compliance_score?.toFixed(1) || 0}%
            </div>
          </motion.div>

          <motion.div
            variants={item}
            className="rounded-xl border border-border bg-card p-5"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Trophy className="h-4 w-4 text-yellow-500" />
              Leader
            </div>
            <div className="mt-2 text-xl font-bold text-foreground truncate">
              {leaderboard[0]?.category || "N/A"}
            </div>
          </motion.div>
        </motion.div>

        {/* Leaderboard Table */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="overflow-hidden rounded-xl border border-border bg-card"
        >
          <div className="px-5 py-4 border-b border-border">
            <h3 className="text-sm font-medium text-foreground">Rankings</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-accent/30">
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground w-16">Rank</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Total Calls</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Avg Score</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Compliance Rate</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Positive Sentiment</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.length > 0 ? (
                  leaderboard.map((entry, i) => (
                    <motion.tr
                      key={entry.category}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.1 + i * 0.05, duration: 0.3 }}
                      className={`border-b border-border/50 transition-colors hover:bg-accent/30 last:border-0 ${
                        entry.rank <= 3 ? 'bg-primary/5' : ''
                      }`}
                    >
                      <td className="px-4 py-3 text-center">
                        {getRankBadge(entry.rank)}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-foreground">
                        {entry.category}
                      </td>
                      <td className="px-4 py-3 text-sm tabular-nums text-muted-foreground">
                        {entry.total_calls}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-16 rounded-full bg-accent overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full"
                              style={{ width: `${entry.avg_compliance_score}%` }}
                            />
                          </div>
                          <span className="text-sm font-semibold tabular-nums text-foreground">
                            {entry.avg_compliance_score.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`rounded-md px-2 py-0.5 text-xs font-medium ${
                          entry.compliance_rate >= 80 
                            ? 'bg-success/10 text-success' 
                            : entry.compliance_rate >= 60 
                            ? 'bg-warning/10 text-warning'
                            : 'bg-destructive/10 text-destructive'
                        }`}>
                          {entry.compliance_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm tabular-nums text-muted-foreground">
                        {entry.positive_sentiment_rate.toFixed(1)}%
                      </td>
                    </motion.tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-sm text-muted-foreground">
                      No data available for this period. Analyze some calls first.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
};

export default Leaderboard;
