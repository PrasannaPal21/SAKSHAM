from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from routers import auth, consent, audit

app = FastAPI(title="SAKSHAM Consent Manager", version="1.0.0")

# CORS - Must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # Explicitly allow localhost
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SAKSHAM Consent Manager API is running"}

from routers import consent, audit #, auth

app.include_router(consent.router)
app.include_router(audit.router)
# app.include_router(auth.router)
