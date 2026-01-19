from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

# --- SHARED MODELS ---

class PurposeLink(BaseModel):
    purpose_code: str
    data_categories: List[str]

# --- REQUEST MODELS ---

class ConsentGrantRequest(BaseModel):
    app_id: str
    purposes: List[PurposeLink]
    expiry_hours: int = 24  # Default expiry
    user_id: Optional[str] = None # In a real app, this comes from JWT, but useful for testing

class ConsentRevokeRequest(BaseModel):
    consent_id: str
    reason: Optional[str] = "User revoked"

class VerifyReceiptRequest(BaseModel):
    receipt: dict # The full JSON receipt

# --- RESPONSE MODELS ---

class ConsentReceiptResponse(BaseModel):
    receipt_id: str
    consent_id: str
    receipt_payload: dict
    signature: str
    timestamp: datetime

class VerificationResponse(BaseModel):
    valid: bool
    status: str # 'active', 'revoked', 'expired', 'invalid_signature'
    message: str
    auditable_event_id: Optional[str] = None

# --- DB MODELS (ReadOnly) ---

class ApplicationRead(BaseModel):
    app_id: str
    app_name: str
    verification_status: str

class ConsentRead(BaseModel):
    consent_id: str
    app_id: str
    status: str
    expiry_time: datetime
