# RLS Troubleshooting Guide

## The Error
```
new row violates row-level security policy for table "consents"
```

## Why This Happens

Row Level Security (RLS) is enabled on your tables, but the policies are blocking inserts. This happens because:

1. **RLS is enabled** but there are no INSERT policies, OR
2. **Backend is using anon key** instead of service_role key (service_role should bypass RLS)
3. **Policies are too restrictive** and don't allow backend operations

## Solutions (Try in Order)

### Solution 1: Run the Updated RLS Policies (Recommended)

1. Go to Supabase Dashboard → SQL Editor
2. Run `backend/fix_rls_policies.sql`
3. This adds policies that allow:
   - Users to manage their own data
   - Backend (service_role) to manage all data

### Solution 2: Verify Backend is Using Service Role Key

**Check your backend `.env` file:**

```bash
cd backend
cat .env
```

**Should contain:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (long key starting with eyJ)
```

**Important:** 
- The `SUPABASE_KEY` should be the **service_role** key (not anon key)
- Service role key is much longer and starts with `eyJ`
- Get it from: Supabase Dashboard → Settings → API → service_role key

**If you're using anon key:**
- Replace it with service_role key in `backend/.env`
- Restart your backend server

### Solution 3: Temporarily Disable RLS (Testing Only)

⚠️ **WARNING: Only for development/testing!**

1. Go to Supabase Dashboard → SQL Editor
2. Run `backend/disable_rls_temporarily.sql`
3. This disables RLS completely (not secure for production!)

### Solution 4: Check if Policies Were Applied

Run this in Supabase SQL Editor to see current policies:

```sql
-- Check policies on consents table
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'consents';
```

You should see policies like:
- "Users can create their own consents"
- "Service role can manage all consents"

## Quick Verification Steps

1. **Check backend .env file:**
   ```bash
   cd backend
   grep SUPABASE_KEY .env
   ```
   Should show service_role key (long, starts with eyJ)

2. **Check if RLS is enabled:**
   ```sql
   SELECT tablename, rowsecurity 
   FROM pg_tables 
   WHERE schemaname = 'public' 
   AND tablename IN ('consents', 'applications', 'audit_events');
   ```

3. **Check policies exist:**
   ```sql
   SELECT policyname, cmd 
   FROM pg_policies 
   WHERE tablename = 'consents';
   ```

## Expected Behavior

- **With service_role key**: RLS should be bypassed automatically
- **With proper policies**: Backend can insert even with anon key
- **Without policies**: Inserts will fail

## Still Not Working?

1. **Restart backend server** after changing .env
2. **Clear browser cache** and try again
3. **Check backend terminal** for detailed error messages
4. **Verify Supabase connection** by checking backend logs

## Production Considerations

For production:
- Use `fix_rls_policies.sql` (not disable_rls_temporarily.sql)
- Always use service_role key in backend
- Keep anon key in frontend only
- Review and test all RLS policies
