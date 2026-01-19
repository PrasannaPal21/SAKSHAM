# SAKSHAM - Backend (Consent Manager)

This directory contains the FastAPI backend for SAKSHAM, responsible for handling consent requests, cryptographic signing, and audit logging.

## Prerequisites

- Python 3.9+
- Supabase Account

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your Supabase credentials:
   ```bash
   cp .env.example .env
   ```
   
   **Required Variables**:
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_KEY`: Your Supabase Service Role Key (or Anon Key if RLS handles everything, but Service Role preferred for admin tasks).

4. **Database Setup**:
   - Run the SQL scripts in `schema.sql` in your Supabase SQL Editor to create the necessary tables.
   - **IMPORTANT**: After running `schema.sql`, also run `fix_rls_policies.sql` to set up Row Level Security policies that allow the backend to insert data.
   
5. **Row Level Security (RLS) Setup**:
   Run `fix_rls_policies.sql` in your Supabase SQL Editor. This is required for the backend to be able to create consents and other records.

## Running the Server

```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **GET /**: Health check.
- **POST /consent/grant**: Grant consent (generates receipt).
- **POST /consent/revoke**: Revoke consent.
- **POST /consent/verify**: Verify a receipt signature and status.
- **GET /audit/events**: Retrieve audit logs (Regulator view).
- **GET /audit/verify-chain**: Verify the cryptographic hash chain integrity.

## Key Files

- `main.py`: App entry point.
- `models.py`: Pydantic data models.
- `utils.py`: Cryptographic functions (RSA signing, SHA-256 hash chaining).
- `routers/`: API route handlers.
