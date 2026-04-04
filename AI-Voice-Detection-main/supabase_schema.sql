-- VoxSentinel Database Schema for Supabase
-- =========================================
-- Run this in your Supabase SQL editor

-- Enable UUID extension (already enabled by default in Supabase)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================
-- CALL ANALYSES TABLE
-- ==========================
-- Stores all analyzed call records

CREATE TABLE IF NOT EXISTS call_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Basic info
  language TEXT NOT NULL DEFAULT 'en',
  transcript TEXT,
  summary TEXT,
  
  -- SOP Validation
  sop_greeting BOOLEAN DEFAULT FALSE,
  sop_identification BOOLEAN DEFAULT FALSE,
  sop_problem_statement BOOLEAN DEFAULT FALSE,
  sop_solution_offering BOOLEAN DEFAULT FALSE,
  sop_closing BOOLEAN DEFAULT FALSE,
  compliance_score DECIMAL(3,2) DEFAULT 0.0,
  adherence_status TEXT DEFAULT 'Non-Compliant' CHECK (adherence_status IN ('Compliant', 'Non-Compliant', 'Partial')),
  sop_explanation TEXT,
  
  -- Analytics
  payment_preference TEXT,
  rejection_reason TEXT,
  sentiment TEXT CHECK (sentiment IN ('Positive', 'Neutral', 'Negative')),
  keywords TEXT[],
  
  -- Metadata
  audio_duration INTEGER, -- in seconds
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_call_analyses_created_at ON call_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_call_analyses_adherence ON call_analyses(adherence_status);
CREATE INDEX IF NOT EXISTS idx_call_analyses_sentiment ON call_analyses(sentiment);

-- ==========================
-- API KEYS TABLE (Optional)
-- ==========================
-- For multi-user API key management

CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  key_hash TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);

-- ==========================
-- API USAGE TABLE (Optional)
-- ==========================
-- For tracking API usage and analytics

CREATE TABLE IF NOT EXISTS api_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL,
  status_code INTEGER,
  response_time_ms INTEGER,
  request_size_bytes INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_usage_created ON api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_key ON api_usage(api_key_id);

-- ==========================
-- ROW LEVEL SECURITY (RLS)
-- ==========================
-- Enable RLS for security (optional, for multi-tenant)

-- ALTER TABLE call_analyses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- ==========================
-- HELPER FUNCTIONS
-- ==========================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for call_analyses
CREATE TRIGGER update_call_analyses_updated_at
  BEFORE UPDATE ON call_analyses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ==========================
-- VIEWS FOR DASHBOARD
-- ==========================

-- Summary stats view
CREATE OR REPLACE VIEW call_stats AS
SELECT 
  COUNT(*) as total_calls,
  AVG(compliance_score) as avg_compliance,
  COUNT(*) FILTER (WHERE adherence_status = 'Compliant') as compliant_calls,
  COUNT(*) FILTER (WHERE adherence_status = 'Non-Compliant') as non_compliant_calls,
  COUNT(*) FILTER (WHERE adherence_status = 'Partial') as partial_calls,
  COUNT(*) FILTER (WHERE sentiment = 'Positive') as positive_sentiment,
  COUNT(*) FILTER (WHERE sentiment = 'Neutral') as neutral_sentiment,
  COUNT(*) FILTER (WHERE sentiment = 'Negative') as negative_sentiment,
  COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE) as calls_today,
  COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as calls_this_week
FROM call_analyses;

-- Daily compliance trend view
CREATE OR REPLACE VIEW daily_compliance_trend AS
SELECT 
  DATE(created_at) as date,
  COUNT(*) as total_calls,
  AVG(compliance_score) as avg_compliance,
  COUNT(*) FILTER (WHERE adherence_status = 'Compliant') as compliant,
  COUNT(*) FILTER (WHERE adherence_status = 'Non-Compliant') as non_compliant
FROM call_analyses
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ==========================
-- SAMPLE DATA (Optional)
-- ==========================
-- Uncomment to insert sample data for testing

/*
INSERT INTO call_analyses (
  language, transcript, summary,
  sop_greeting, sop_identification, sop_problem_statement, 
  sop_solution_offering, sop_closing,
  compliance_score, adherence_status, sop_explanation,
  payment_preference, rejection_reason, sentiment,
  keywords
) VALUES
(
  'en',
  'Hello, this is Sarah from customer service. How may I help you today? I understand you are having issues with your payment. Let me help you resolve this by offering a flexible payment plan. Is there anything else I can help you with? Thank you for calling.',
  'Customer called about payment issues. Agent offered flexible payment plan and resolved the issue.',
  true, true, true, true, true,
  1.0, 'Compliant', 'All SOP requirements were met during the call.',
  'Credit Card', NULL, 'Positive',
  ARRAY['payment', 'flexible plan', 'customer service']
),
(
  'hi',
  'नमस्ते, मैं ग्राहक सेवा से बात कर रही हूं। क्या मैं आपकी मदद कर सकती हूं?',
  'Hindi language call with proper greeting and identification.',
  true, true, false, false, false,
  0.4, 'Non-Compliant', 'Missing problem statement, solution offering, and closing.',
  NULL, 'High Price', 'Neutral',
  ARRAY['greeting', 'customer service']
);
*/

-- ==========================
-- PERMISSIONS
-- ==========================
-- Grant permissions for authenticated users (if using Supabase Auth)

-- GRANT SELECT, INSERT, UPDATE ON call_analyses TO authenticated;
-- GRANT SELECT ON call_stats TO authenticated;
-- GRANT SELECT ON daily_compliance_trend TO authenticated;
