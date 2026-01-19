# Understanding the CORS and 500 Error

## The Errors You Encountered

1. **CORS Error**: `Access to fetch at 'http://127.0.0.1:8000/consent/grant' from origin 'http://localhost:5173' has been blocked by CORS policy`
2. **500 Internal Server Error**: `POST http://127.0.0.1:8000/consent/grant net::ERR_FAILED 500`

## Why These Errors Occurred

### CORS Error Explanation

**CORS (Cross-Origin Resource Sharing)** is a browser security feature that blocks requests from one origin (domain/port) to another unless the server explicitly allows it.

- **Frontend**: Running on `http://localhost:5173` (Vite dev server)
- **Backend**: Running on `http://127.0.0.1:8000` (FastAPI server)
- Even though both are localhost, browsers treat different ports as different origins

**Why you saw this error:**
- When the backend returns a 500 error, it might not include CORS headers
- The browser blocks the response before you can see the actual error
- This makes debugging harder

### 500 Internal Server Error - Root Causes

The backend was crashing due to several issues:

1. **Authentication Error Handling**: The `get_current_user` function wasn't handling exceptions properly when Supabase auth failed
2. **Database Query Error**: The code tried to access `last_event.data[0]` without checking if the list was empty
3. **Missing Error Handling**: No try-catch blocks to handle database or other errors gracefully
4. **Poor Error Messages**: Errors weren't being logged, making debugging difficult

## What Was Fixed

### 1. Improved CORS Configuration (`backend/main.py`)
```python
# Before: allow_origins=["*"]
# After: Explicitly allow localhost origins
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"]
```

### 2. Better Authentication Error Handling (`backend/routers/auth.py`)
- Added try-catch block around Supabase auth calls
- Better error messages
- Proper token validation

### 3. Fixed Database Query Issues (`backend/routers/consent.py`)
- Added proper checks for empty query results
- Wrapped hash chain queries in try-catch
- Better handling when no audit events exist yet

### 4. Comprehensive Error Handling (`backend/routers/consent.py`)
- Wrapped entire function in try-catch
- Logs full error traceback for debugging
- Returns proper HTTP error responses

### 5. Better Frontend Error Display (`src/components/AdminDashboard.jsx`)
- Catches and displays actual error messages
- Shows HTTP status codes
- Better user feedback

## How to Debug Similar Issues in the Future

### 1. Check Backend Logs
Always check your backend terminal for error messages. The fixes now include detailed logging:
```python
print(f"Error in grant_consent: {error_details}")
```

### 2. Check Browser Console
- Open Developer Tools (F12)
- Go to Console tab
- Look for detailed error messages

### 3. Check Network Tab
- Open Developer Tools → Network tab
- Find the failed request
- Check:
  - Request headers (is Authorization header present?)
  - Response status code
  - Response body (click on the request to see details)

### 4. Test Backend Directly
Use curl or Postman to test the API directly:
```bash
curl -X POST http://127.0.0.1:8000/consent/grant \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"app_id": "test", "purposes": [{"purpose_code": "CORE_FUNCTION", "data_categories": ["email"]}], "expiry_hours": 24}'
```

### 5. Verify Environment Variables
Make sure your `.env` files are set up correctly:
- Backend: `SUPABASE_URL` and `SUPABASE_KEY` (service_role key)
- Frontend: `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` (anon key)

## Common Issues and Solutions

### Issue: "Missing Authorization Header"
**Solution**: Make sure you're logged in and the token is being passed correctly

### Issue: "Invalid Authentication Token"
**Solution**: 
- Check if your Supabase credentials are correct
- Verify the user exists in Supabase
- Make sure you're using the correct key (service_role for backend, anon for frontend)

### Issue: "Failed to create consent record"
**Solution**:
- Check if database tables exist (run schema.sql)
- Verify database connection
- Check Supabase logs

### Issue: CORS still blocking
**Solution**:
- Make sure backend is running
- Restart backend after changing CORS settings
- Check that both frontend and backend are using the same protocol (http vs https)

## Testing the Fixes

After these fixes, you should:
1. Restart your backend server
2. Try the consent grant request again
3. Check backend terminal for any error messages
4. Check browser console for detailed error messages if it still fails

The errors should now be more descriptive and help you identify the exact issue.
