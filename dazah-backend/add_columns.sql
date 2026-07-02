-- Add missing columns to sop_ai_check_main
ALTER TABLE public.sop_ai_check_main 
ADD COLUMN IF NOT EXISTS risk_high INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS risk_medium INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS risk_low INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_problems INTEGER DEFAULT 0;