-- TEMPORARY FIX: Disable RLS for testing
-- ⚠️ WARNING: This disables RLS security. Only use for development/testing!
-- For production, use fix_rls_policies.sql instead

-- Disable RLS on all tables (temporary for testing)
ALTER TABLE consents DISABLE ROW LEVEL SECURITY;
ALTER TABLE applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE consent_purposes DISABLE ROW LEVEL SECURITY;
ALTER TABLE consent_receipts DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY;
ALTER TABLE purposes DISABLE ROW LEVEL SECURITY;

-- To re-enable RLS later, run fix_rls_policies.sql
