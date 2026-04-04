import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  ArrowLeft, Lightbulb, Users, Download, AlertCircle, 
  CheckCircle, Info, Loader2, MessageSquare 
} from "lucide-react";
import PageTransition from "@/components/PageTransition";
import { useCallById, useRecommendations, useDiarization, useExportCsv } from "@/hooks/useApi";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

const priorityColors = {
  high: 'bg-destructive/10 text-destructive border-destructive/20',
  medium: 'bg-warning/10 text-warning border-warning/20',
  low: 'bg-success/10 text-success border-success/20',
};

const priorityIcons = {
  high: AlertCircle,
  medium: Info,
  low: CheckCircle,
};

const CallDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'recommendations' | 'diarization'>('recommendations');
  
  const { data: callData, isLoading: callLoading } = useCallById(id || '');
  const { data: recsData, isLoading: recsLoading } = useRecommendations(id || '');
  const { data: diarData, isLoading: diarLoading } = useDiarization(id || '');
  const exportCsv = useExportCsv();

  if (callLoading) {
    return (
      <PageTransition>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-muted-foreground">Loading call details...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  const call = callData?.call;
  const recommendations = recsData?.recommendations || [];
  const diarization = diarData;

  if (!call) {
    return (
      <PageTransition>
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <AlertCircle className="mx-auto h-8 w-8 text-destructive" />
            <p className="mt-2 text-sm text-muted-foreground">Call not found</p>
            <button 
              onClick={() => navigate('/history')}
              className="mt-4 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md"
            >
              Back to History
            </button>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/history')}
              className="p-2 rounded-md hover:bg-accent transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-foreground">
                Call Analysis
              </h1>
              <p className="text-sm text-muted-foreground font-mono">
                {call.id}
              </p>
            </div>
          </div>
          <button
            onClick={() => id && exportCsv.mutate(id)}
            disabled={exportCsv.isPending}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {exportCsv.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            Export CSV
          </button>
        </div>

        {/* Call Summary Card */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 sm:grid-cols-4 gap-4"
        >
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs text-muted-foreground">Language</div>
            <div className="mt-1 text-lg font-semibold text-foreground uppercase">
              {call.language}
            </div>
          </motion.div>
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs text-muted-foreground">Compliance</div>
            <div className="mt-1 text-lg font-semibold text-foreground">
              {(call.compliance_score * 100).toFixed(0)}%
            </div>
          </motion.div>
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs text-muted-foreground">Status</div>
            <div className={`mt-1 text-lg font-semibold ${
              call.adherence_status === 'Compliant' ? 'text-success' :
              call.adherence_status === 'Non-Compliant' ? 'text-destructive' : 'text-warning'
            }`}>
              {call.adherence_status}
            </div>
          </motion.div>
          <motion.div variants={item} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs text-muted-foreground">Sentiment</div>
            <div className={`mt-1 text-lg font-semibold ${
              call.sentiment === 'Positive' ? 'text-success' :
              call.sentiment === 'Negative' ? 'text-destructive' : 'text-muted-foreground'
            }`}>
              {call.sentiment}
            </div>
          </motion.div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-border pb-2">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-t-md transition-colors ${
              activeTab === 'recommendations'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Lightbulb className="h-4 w-4" />
            AI Recommendations
            {recsData && (
              <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-background/20">
                {recsData.high_priority}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('diarization')}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-t-md transition-colors ${
              activeTab === 'diarization'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Users className="h-4 w-4" />
            Speaker Diarization
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'recommendations' && (
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-4"
          >
            {recsLoading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : recommendations.length > 0 ? (
              recommendations.map((rec, i) => {
                const Icon = priorityIcons[rec.priority];
                return (
                  <motion.div
                    key={i}
                    variants={item}
                    className={`rounded-xl border p-5 ${priorityColors[rec.priority]}`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="mt-0.5">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{rec.category}</h4>
                          <span className={`text-xs px-2 py-0.5 rounded-full uppercase ${
                            rec.priority === 'high' ? 'bg-destructive text-destructive-foreground' :
                            rec.priority === 'medium' ? 'bg-warning text-warning-foreground' :
                            'bg-success text-success-foreground'
                          }`}>
                            {rec.priority}
                          </span>
                        </div>
                        <p className="mt-1 text-sm opacity-80">{rec.issue}</p>
                        <div className="mt-3 p-3 rounded-lg bg-background/50">
                          <p className="text-sm font-medium">💡 Suggestion</p>
                          <p className="mt-1 text-sm opacity-80">{rec.suggestion}</p>
                        </div>
                        <p className="mt-2 text-xs opacity-60">
                          📊 Impact: {rec.impact}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })
            ) : (
              <div className="rounded-xl border border-border bg-card p-8 text-center">
                <CheckCircle className="mx-auto h-8 w-8 text-success" />
                <p className="mt-2 text-sm text-muted-foreground">
                  No recommendations - great job!
                </p>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'diarization' && (
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-4"
          >
            {diarLoading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : diarization ? (
              <>
                {/* Speaker Stats */}
                <motion.div
                  variants={item}
                  className="grid grid-cols-3 gap-4"
                >
                  <div className="rounded-xl border border-border bg-card p-4">
                    <div className="text-xs text-muted-foreground">Agent Speaking</div>
                    <div className="mt-1 text-2xl font-bold text-primary">
                      {diarization.agent_percentage}%
                    </div>
                  </div>
                  <div className="rounded-xl border border-border bg-card p-4">
                    <div className="text-xs text-muted-foreground">Customer Speaking</div>
                    <div className="mt-1 text-2xl font-bold text-foreground">
                      {diarization.customer_percentage}%
                    </div>
                  </div>
                  <div className="rounded-xl border border-border bg-card p-4">
                    <div className="text-xs text-muted-foreground">Total Turns</div>
                    <div className="mt-1 text-2xl font-bold text-muted-foreground">
                      {diarization.total_turns || 'N/A'}
                    </div>
                  </div>
                </motion.div>

                {/* Speaking Time Bar */}
                <motion.div variants={item} className="rounded-xl border border-border bg-card p-4">
                  <div className="text-xs text-muted-foreground mb-2">Speaking Distribution</div>
                  <div className="h-4 rounded-full overflow-hidden flex bg-accent">
                    <div 
                      className="bg-primary transition-all duration-500"
                      style={{ width: `${diarization.agent_percentage}%` }}
                    />
                    <div 
                      className="bg-muted-foreground"
                      style={{ width: `${diarization.customer_percentage}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-primary" />
                      Agent
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="h-2 w-2 rounded-full bg-muted-foreground" />
                      Customer
                    </span>
                  </div>
                </motion.div>

                {/* Diarized Transcript */}
                <motion.div variants={item} className="rounded-xl border border-border bg-card p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    <h4 className="font-medium">Diarized Transcript</h4>
                  </div>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {diarization.diarized_transcript.split('\n\n').map((segment, i) => {
                      const isAgent = segment.startsWith('Agent:');
                      return (
                        <div
                          key={i}
                          className={`p-3 rounded-lg ${
                            isAgent 
                              ? 'bg-primary/10 border-l-2 border-primary' 
                              : 'bg-accent border-l-2 border-muted-foreground'
                          }`}
                        >
                          <p className="text-sm">{segment}</p>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              </>
            ) : (
              <div className="rounded-xl border border-border bg-card p-8 text-center">
                <Users className="mx-auto h-8 w-8 text-muted-foreground" />
                <p className="mt-2 text-sm text-muted-foreground">
                  Diarization not available
                </p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </PageTransition>
  );
};

export default CallDetail;
