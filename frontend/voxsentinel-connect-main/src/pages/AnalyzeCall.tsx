import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, CheckCircle2, Loader2, FileAudio, AlertCircle, XCircle } from "lucide-react";
import PageTransition from "@/components/PageTransition";
import { useAnalyzeCall } from "@/hooks/useApi";
import { AnalysisResult } from "@/lib/api";

const steps = [
  { label: "Uploading Audio", description: "Sending audio to server..." },
  { label: "Transcribing", description: "Converting speech to text with Whisper AI..." },
  { label: "Analyzing Compliance", description: "Evaluating against SOP framework..." },
];

const AnalyzeCall = () => {
  const [dragOver, setDragOver] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("en");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const analyzeCall = useAnalyzeCall();
  const { isPending: processing, isError, error, isSuccess } = analyzeCall;

  const processFile = useCallback(async (file: File) => {
    // Validate file type
    const validTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/x-m4a', 'audio/mp4'];
    if (!validTypes.some(type => file.type.includes(type.split('/')[1]))) {
      alert('Please upload a valid audio file (WAV, MP3, or M4A)');
      return;
    }
    
    // Validate file size (100MB max)
    if (file.size > 100 * 1024 * 1024) {
      alert('File size must be less than 100MB');
      return;
    }
    
    setSelectedFile(file);
    setCurrentStep(0);
    setAnalysisResult(null);
    
    // Simulate step progression while API runs
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < steps.length - 1) return prev + 1;
        return prev;
      });
    }, 2000);
    
    try {
      const result = await analyzeCall.mutateAsync({ file, language });
      setAnalysisResult(result);
    } finally {
      clearInterval(stepInterval);
      setCurrentStep(steps.length);
    }
  }, [analyzeCall, language]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file && !processing) {
        processFile(file);
      }
    },
    [processing, processFile]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && !processing) {
      processFile(file);
    }
  };

  const handleClick = () => {
    if (!processing && !isSuccess) {
      fileInputRef.current?.click();
    }
  };

  const reset = () => {
    setCurrentStep(-1);
    setSelectedFile(null);
    setAnalysisResult(null);
    analyzeCall.reset();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getComplianceColor = (score: number) => {
    if (score >= 0.8) return 'text-success';
    if (score >= 0.6) return 'text-warning';
    return 'text-destructive';
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">Analyze Call</h1>
            <p className="text-sm text-muted-foreground">Upload a call recording for compliance analysis</p>
          </div>
          
          {/* Language selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
            disabled={processing}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </select>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileSelect}
          className="hidden"
        />

        <AnimatePresence mode="wait">
          {!processing && !isSuccess && !isError && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              onDragEnter={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={handleClick}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-16 transition-all ${
                dragOver
                  ? "border-primary bg-primary/5 scale-[1.01]"
                  : "border-border hover:border-muted-foreground/30 hover:bg-accent/30"
              }`}
            >
              <motion.div animate={dragOver ? { scale: 1.15 } : { scale: 1 }} transition={{ type: "spring", stiffness: 300 }}>
                <Upload className={`h-12 w-12 ${dragOver ? "text-primary" : "text-muted-foreground"}`} />
              </motion.div>
              <p className="mt-4 text-sm font-medium text-foreground">Drop your audio file here</p>
              <p className="mt-1 text-xs text-muted-foreground">or click to browse · WAV, MP3, M4A up to 100MB</p>
            </motion.div>
          )}

          {processing && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="rounded-xl border border-border bg-card p-8"
            >
              <div className="mb-6 flex items-center gap-3">
                <FileAudio className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium text-foreground">
                  Processing {selectedFile?.name || 'audio file'}
                </span>
              </div>
              <div className="space-y-4">
                {steps.map((step, i) => {
                  const isActive = i === currentStep;
                  const isComplete = i < currentStep;
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1, duration: 0.3 }}
                      className="flex items-start gap-3"
                    >
                      <div className="mt-0.5">
                        {isComplete ? (
                          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 400 }}>
                            <CheckCircle2 className="h-5 w-5 text-success" />
                          </motion.div>
                        ) : isActive ? (
                          <Loader2 className="h-5 w-5 animate-spin text-primary" />
                        ) : (
                          <div className="h-5 w-5 rounded-full border-2 border-border" />
                        )}
                      </div>
                      <div>
                        <div className={`text-sm font-medium ${isActive ? "text-foreground" : isComplete ? "text-muted-foreground" : "text-muted-foreground/50"}`}>
                          {i + 1}. {step.label}
                        </div>
                        {(isActive || isComplete) && (
                          <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xs text-muted-foreground"
                          >
                            {step.description}
                          </motion.p>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          )}

          {isError && (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="rounded-xl border border-destructive/50 bg-destructive/10 p-8 text-center"
            >
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 300 }}>
                <XCircle className="mx-auto h-16 w-16 text-destructive" />
              </motion.div>
              <h3 className="mt-4 text-lg font-semibold text-foreground">Analysis Failed</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {error?.message || 'An error occurred during analysis. Please try again.'}
              </p>
              <button
                onClick={reset}
                className="mt-6 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 active:scale-[0.98]"
              >
                Try Again
              </button>
            </motion.div>
          )}

          {isSuccess && analysisResult && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-6"
            >
              {/* Success header */}
              <div className="rounded-xl border border-border bg-card p-8 text-center">
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 300, delay: 0.1 }}>
                  <CheckCircle2 className="mx-auto h-16 w-16 text-success" />
                </motion.div>
                <h3 className="mt-4 text-lg font-semibold text-foreground">Analysis Complete</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Compliance score: 
                  <span className={`ml-1 font-semibold tabular-nums ${getComplianceColor(analysisResult.sop_validation.complianceScore)}`}>
                    {(analysisResult.sop_validation.complianceScore * 100).toFixed(1)}%
                  </span>
                </p>
                
                {/* Status badge */}
                <div className="mt-3">
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
                    analysisResult.sop_validation.adherenceStatus === 'Compliant' 
                      ? 'bg-success/20 text-success'
                      : analysisResult.sop_validation.adherenceStatus === 'Partial'
                      ? 'bg-warning/20 text-warning'
                      : 'bg-destructive/20 text-destructive'
                  }`}>
                    {analysisResult.sop_validation.adherenceStatus}
                  </span>
                </div>
              </div>
              
              {/* SOP Validation Grid */}
              <div className="rounded-xl border border-border bg-card p-6">
                <h4 className="mb-4 text-sm font-semibold text-foreground">SOP Compliance Checklist</h4>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-5">
                  {[
                    { label: "Greeting", passed: analysisResult.sop_validation.greeting },
                    { label: "Identification", passed: analysisResult.sop_validation.identification },
                    { label: "Problem Statement", passed: analysisResult.sop_validation.problemStatement },
                    { label: "Solution Offering", passed: analysisResult.sop_validation.solutionOffering },
                    { label: "Closing", passed: analysisResult.sop_validation.closing },
                  ].map((item) => (
                    <div key={item.label} className="rounded-lg bg-accent p-3 text-center">
                      <div className="mb-2">
                        {item.passed ? (
                          <CheckCircle2 className="mx-auto h-6 w-6 text-success" />
                        ) : (
                          <AlertCircle className="mx-auto h-6 w-6 text-destructive" />
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">{item.label}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Analytics */}
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-xl border border-border bg-card p-4">
                  <div className="text-xs text-muted-foreground">Sentiment</div>
                  <div className={`mt-1 text-lg font-semibold ${
                    analysisResult.analytics.sentiment === 'Positive' ? 'text-success' :
                    analysisResult.analytics.sentiment === 'Negative' ? 'text-destructive' : 'text-muted-foreground'
                  }`}>
                    {analysisResult.analytics.sentiment}
                  </div>
                </div>
                <div className="rounded-xl border border-border bg-card p-4">
                  <div className="text-xs text-muted-foreground">Payment Preference</div>
                  <div className="mt-1 text-lg font-semibold text-foreground">
                    {analysisResult.analytics.paymentPreference || 'N/A'}
                  </div>
                </div>
                <div className="rounded-xl border border-border bg-card p-4">
                  <div className="text-xs text-muted-foreground">Rejection Reason</div>
                  <div className="mt-1 text-lg font-semibold text-foreground">
                    {analysisResult.analytics.rejectionReason || 'N/A'}
                  </div>
                </div>
              </div>
              
              {/* Summary */}
              <div className="rounded-xl border border-border bg-card p-6">
                <h4 className="mb-2 text-sm font-semibold text-foreground">Summary</h4>
                <p className="text-sm text-muted-foreground">{analysisResult.summary}</p>
              </div>
              
              {/* Transcript */}
              <div className="rounded-xl border border-border bg-card p-6">
                <h4 className="mb-2 text-sm font-semibold text-foreground">Transcript</h4>
                <p className="max-h-48 overflow-y-auto whitespace-pre-wrap text-sm text-muted-foreground">
                  {analysisResult.transcript}
                </p>
              </div>
              
              {/* Keywords */}
              {analysisResult.keywords && analysisResult.keywords.length > 0 && (
                <div className="rounded-xl border border-border bg-card p-6">
                  <h4 className="mb-2 text-sm font-semibold text-foreground">Keywords</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.keywords.map((keyword, i) => (
                      <span key={i} className="rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              <div className="rounded-xl border border-border bg-card p-6">
                <h4 className="mb-2 text-sm font-semibold text-foreground">Compliance Explanation</h4>
                <p className="text-sm text-muted-foreground">{analysisResult.sop_validation.explanation}</p>
              </div>
              
              <button
                onClick={reset}
                className="w-full rounded-md bg-primary px-4 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 active:scale-[0.99]"
              >
                Analyze Another Call
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  );
};

export default AnalyzeCall;
