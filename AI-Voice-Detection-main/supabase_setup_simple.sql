-- VoxSentinel Database Schema - COPY THIS ENTIRE FILE AND PASTE IN SUPABASE SQL EDITOR
-- Then click "Run" button

-- Step 1: Create the main call_analyses table
CREATE TABLE IF NOT EXISTS call_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  language TEXT NOT NULL DEFAULT 'en',
  transcript TEXT,
  summary TEXT,
  sop_greeting BOOLEAN DEFAULT FALSE,
  sop_identification BOOLEAN DEFAULT FALSE,
  sop_problem_statement BOOLEAN DEFAULT FALSE,
  sop_solution_offering BOOLEAN DEFAULT FALSE,
  sop_closing BOOLEAN DEFAULT FALSE,
  compliance_score DECIMAL(3,2) DEFAULT 0.0,
  adherence_status TEXT DEFAULT 'Non-Compliant' CHECK (adherence_status IN ('Compliant', 'Non-Compliant', 'Partial')),
  sop_explanation TEXT,
  payment_preference TEXT,
  rejection_reason TEXT,
  sentiment TEXT CHECK (sentiment IN ('Positive', 'Neutral', 'Negative')),
  keywords TEXT[],
  audio_duration INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 2: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_call_analyses_created_at ON call_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_call_analyses_adherence ON call_analyses(adherence_status);
CREATE INDEX IF NOT EXISTS idx_call_analyses_sentiment ON call_analyses(sentiment);

-- Step 3: Create update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_call_analyses_updated_at
  BEFORE UPDATE ON call_analyses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Step 4: Insert sample data for testing
INSERT INTO call_analyses (
  language, transcript, summary,
  sop_greeting, sop_identification, sop_problem_statement, 
  sop_solution_offering, sop_closing,
  compliance_score, adherence_status, sop_explanation,
  payment_preference, rejection_reason, sentiment, keywords
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
  'नमस्ते, मैं आपकी सेवा में हूं। क्या मैं आपकी कोई मदद कर सकती हूं?',
  'Hindi language call - basic greeting provided.',
  true, false, false, false, false,
  0.2, 'Non-Compliant', 'Missing identification, problem statement, solution, and closing.',
  NULL, 'High Price', 'Neutral',
  ARRAY['greeting', 'service']
),
(
  'ta',
  'வணக்கம், நான் வாடிக்கையாளர் சேவையில் இருந்து பேசுகிறேன். உங்களுக்கு என்ன உதவி வேண்டும்?',
  'Tamil language call - proper greeting and identification.',
  true, true, false, false, false,
  0.4, 'Partial', 'Good start but incomplete conversation flow.',
  NULL, NULL, 'Positive',
  ARRAY['greeting', 'customer service', 'help']
);

-- Done! You should see "Success. No rows returned" if everything worked.
