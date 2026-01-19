-- Fix RLS Policies for SAKSHAM
-- Run this in your Supabase SQL Editor

-- ============================================================================
-- CONSENTS TABLE POLICIES
-- ============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own consents" ON consents;
DROP POLICY IF EXISTS "Users can create their own consents" ON consents;
DROP POLICY IF EXISTS "Users can update their own consents" ON consents;
DROP POLICY IF EXISTS "Service role can manage all consents" ON consents;

-- Allow users to SELECT their own consents
CREATE POLICY "Users can view their own consents"
ON consents FOR SELECT
USING (auth.uid() = user_id);

-- Allow users to INSERT their own consents
CREATE POLICY "Users can create their own consents"
ON consents FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Allow users to UPDATE (revoke) their own consents
CREATE POLICY "Users can update their own consents"
ON consents FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- IMPORTANT: Allow service_role (backend) to bypass RLS for all operations
-- This policy allows the backend using service_role key to perform any operation
-- The service_role key should bypass RLS, but this ensures it works
CREATE POLICY "Service role can manage all consents"
ON consents FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================================================
-- APPLICATIONS TABLE POLICIES
-- ============================================================================

-- Enable RLS on applications
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Anyone can view applications" ON applications;
DROP POLICY IF EXISTS "Authenticated users can create applications" ON applications;
DROP POLICY IF EXISTS "Service role can manage all applications" ON applications;

-- Allow users to view applications (needed for consent creation)
CREATE POLICY "Anyone can view applications"
ON applications FOR SELECT
USING (true);

-- Allow authenticated users to create applications
CREATE POLICY "Authenticated users can create applications"
ON applications FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Allow service_role (backend) to manage applications
CREATE POLICY "Service role can manage all applications"
ON applications FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================================================
-- CONSENT_PURPOSES TABLE POLICIES
-- ============================================================================

-- Enable RLS on consent_purposes
ALTER TABLE consent_purposes ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view purposes for their consents" ON consent_purposes;
DROP POLICY IF EXISTS "Users can create purposes for their consents" ON consent_purposes;
DROP POLICY IF EXISTS "Service role can manage all consent purposes" ON consent_purposes;

-- Allow users to view purposes for their own consents
CREATE POLICY "Users can view purposes for their consents"
ON consent_purposes FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM consents 
        WHERE consents.consent_id = consent_purposes.consent_id 
        AND consents.user_id = auth.uid()
    )
);

-- Allow users to insert purposes for their own consents
CREATE POLICY "Users can create purposes for their consents"
ON consent_purposes FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM consents 
        WHERE consents.consent_id = consent_purposes.consent_id 
        AND consents.user_id = auth.uid()
    )
);

-- Allow service_role (backend) to manage consent purposes
CREATE POLICY "Service role can manage all consent purposes"
ON consent_purposes FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================================================
-- CONSENT_RECEIPTS TABLE POLICIES
-- ============================================================================

-- Enable RLS on consent_receipts
ALTER TABLE consent_receipts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view receipts for their consents" ON consent_receipts;
DROP POLICY IF EXISTS "Users can create receipts for their consents" ON consent_receipts;
DROP POLICY IF EXISTS "Service role can manage all consent receipts" ON consent_receipts;

-- Allow users to view receipts for their own consents
CREATE POLICY "Users can view receipts for their consents"
ON consent_receipts FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM consents 
        WHERE consents.consent_id = consent_receipts.consent_id 
        AND consents.user_id = auth.uid()
    )
);

-- Allow users to insert receipts for their own consents
CREATE POLICY "Users can create receipts for their consents"
ON consent_receipts FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM consents 
        WHERE consents.consent_id = consent_receipts.consent_id 
        AND consents.user_id = auth.uid()
    )
);

-- Allow service_role (backend) to manage consent receipts
CREATE POLICY "Service role can manage all consent receipts"
ON consent_receipts FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================================================
-- AUDIT_EVENTS TABLE POLICIES
-- ============================================================================

-- Enable RLS on audit_events
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view their own audit events" ON audit_events;
DROP POLICY IF EXISTS "Authenticated users can create audit events" ON audit_events;
DROP POLICY IF EXISTS "Service role can manage all audit events" ON audit_events;

-- Allow users to view their own audit events
CREATE POLICY "Users can view their own audit events"
ON audit_events FOR SELECT
USING (auth.uid() = actor_id);

-- Allow authenticated users to insert audit events
CREATE POLICY "Authenticated users can create audit events"
ON audit_events FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Allow service_role (backend) to manage audit events
CREATE POLICY "Service role can manage all audit events"
ON audit_events FOR ALL
USING (true)
WITH CHECK (true);

-- ============================================================================
-- PURPOSES TABLE (No RLS needed - public reference data)
-- ============================================================================

-- Purposes table contains public reference data, no RLS needed
-- But we'll enable it for consistency and add a permissive policy
ALTER TABLE purposes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view purposes"
ON purposes FOR SELECT
USING (true);
