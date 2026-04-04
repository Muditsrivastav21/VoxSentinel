import { useState } from "react";
import { motion } from "framer-motion";
import { Eye, Loader2, ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import PageTransition from "@/components/PageTransition";
import { useCallHistory, useDeleteCall } from "@/hooks/useApi";

const statusColor = (status: string) => {
  switch (status) {
    case "Compliant": return "text-success bg-success/10";
    case "Flagged": 
    case "Non-Compliant": return "text-destructive bg-destructive/10";
    default: return "text-warning bg-warning/10";
  }
};

const sentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case "Positive": return "text-success";
    case "Negative": return "text-destructive";
    default: return "text-muted-foreground";
  }
};

const CallHistory = () => {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const perPage = 10;
  
  const { data, isLoading, isError, error } = useCallHistory(page, perPage);
  const deleteCall = useDeleteCall();
  
  const calls = data?.calls || [];
  const totalCalls = data?.total || 0;
  const totalPages = Math.ceil(totalCalls / perPage) || 1;
  
  // Filter by search
  const filteredCalls = calls.filter(call => 
    call.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    call.language.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (call.adherence_status || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete this call?")) {
      deleteCall.mutate(id);
    }
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">Call History</h1>
            <p className="text-sm text-muted-foreground">Browse and review all analyzed calls</p>
            {isError && (
              <p className="mt-1 text-xs text-warning">
                ⚠️ Failed to fetch - {error?.message || "Backend may be offline"}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search calls..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            />
          </div>
        </div>

        {isLoading ? (
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="overflow-hidden rounded-xl border border-border bg-card">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-accent/30">
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">ID</th>
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">Language</th>
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">Date</th>
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">Sentiment</th>
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">Score</th>
                      <th className="sticky top-0 px-4 py-3 text-left text-xs font-medium text-muted-foreground">Status</th>
                      <th className="sticky top-0 px-4 py-3 text-right text-xs font-medium text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCalls.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-4 py-8 text-center text-sm text-muted-foreground">
                          {calls.length === 0 
                            ? "No calls analyzed yet. Go to \"Analyze Call\" to analyze your first call."
                            : "No calls match your search criteria."
                          }
                        </td>
                      </tr>
                    ) : (
                      filteredCalls.map((call, i) => (
                        <motion.tr
                          key={call.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: i * 0.04, duration: 0.3 }}
                          className="group border-b border-border/50 transition-colors hover:bg-accent/30 last:border-0"
                        >
                          <td className="px-4 py-3 text-sm font-mono text-muted-foreground">{call.id.slice(0, 8)}</td>
                          <td className="px-4 py-3 text-sm font-medium uppercase text-foreground">{call.language}</td>
                          <td className="px-4 py-3 text-sm tabular-nums text-muted-foreground">
                            {new Date(call.created_at).toLocaleString()}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-sm font-medium ${sentimentColor(call.sentiment)}`}>
                              {call.sentiment}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm font-semibold tabular-nums text-foreground">
                            {Math.round(call.compliance_score * 100)}%
                          </td>
                          <td className="px-4 py-3">
                            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(call.adherence_status || 'Non-Compliant')}`}>
                              {call.adherence_status || 'Non-Compliant'}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center justify-end gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                              <button 
                                className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground active:scale-95"
                                title="View details"
                              >
                                <Eye className="h-3.5 w-3.5" />
                              </button>
                              <button 
                                className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive active:scale-95"
                                title="Delete"
                                onClick={() => handleDelete(call.id)}
                                disabled={deleteCall.isPending}
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </td>
                        </motion.tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Showing {((page - 1) * perPage) + 1} - {Math.min(page * perPage, totalCalls)} of {totalCalls}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-md border border-border p-2 text-muted-foreground transition-colors hover:bg-accent disabled:opacity-50"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <span className="text-sm">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="rounded-md border border-border p-2 text-muted-foreground transition-colors hover:bg-accent disabled:opacity-50"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </PageTransition>
  );
};

export default CallHistory;
