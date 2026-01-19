from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta
import json
import uuid

from database import get_db
from models import (
    ConsentGrantRequest, ConsentReceiptResponse, 
    VerifyReceiptRequest, VerificationResponse, ConsentRevokeRequest
)
from routers.auth import get_current_user
from utils import sign_payload, generate_hash_chain, verify_signature

router = APIRouter(prefix="/consent", tags=["Consent"])

@router.post("/grant", response_model=ConsentReceiptResponse)
async def grant_consent(request: ConsentGrantRequest, user = Depends(get_current_user)):
    """
    User grants consent to an App.
    Generates a signed receipt and logs the audit event.
    """
    try:
        db = get_db()
        
        # 1. Resolve App ID (handle both UUID and text identifiers)
        app_id = request.app_id
        
        # Check if app_id is a valid UUID
        try:
            uuid.UUID(app_id)
            # It's a valid UUID, check if application exists
            app_check = db.table("applications").select("app_id").eq("app_id", app_id).execute()
            if not app_check.data or len(app_check.data) == 0:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Application with ID {app_id} not found. Please create the application first."
                )
        except ValueError:
            # Not a valid UUID, treat as app identifier/name
            # Look up by app_name or create new application
            app_lookup = db.table("applications").select("app_id").eq("app_name", app_id).execute()
            
            if app_lookup.data and len(app_lookup.data) > 0:
                # Application exists, use its UUID
                app_id = app_lookup.data[0]['app_id']
            else:
                # Create new application with this identifier as name
                new_app = db.table("applications").insert({
                    "app_name": app_id,
                    "owner_user_id": user.id if user else None,
                    "verification_status": "pending"
                }).execute()
                
                if not new_app.data:
                    raise HTTPException(status_code=500, detail="Failed to create application record")
                
                app_id = new_app.data[0]['app_id']
        
        # 2. Create Consent Record
        expiry_time = datetime.utcnow() + timedelta(hours=request.expiry_hours)
        
        # Use user.id from auth token in production, for now allow request override for testing or use auth
        user_id = user.id if user else request.user_id 
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")

        consent_data = {
            "user_id": user_id,
            "app_id": app_id,  # Now guaranteed to be a valid UUID
            "expiry_time": expiry_time.isoformat(),
            "status": "active"
        }
        
        # Insert into 'consents'
        res = db.table("consents").insert(consent_data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create consent record")
        
        consent_id = res.data[0]['consent_id']
        
        # 3. Add Purposes
        pk_purposes = []
        receipt_purposes = []
        
        for p in request.purposes:
            pk_purposes.append({
                "consent_id": consent_id,
                "purpose_code": p.purpose_code,
                "data_categories": p.data_categories
            })
            receipt_purposes.append({
                "purpose": p.purpose_code,
                "categories": p.data_categories
            })
            
        db.table("consent_purposes").insert(pk_purposes).execute()
        
        # 4. Generate Receipt Payload
        # Get app name for receipt (for readability)
        app_info = db.table("applications").select("app_name").eq("app_id", app_id).execute()
        app_name = app_info.data[0]['app_name'] if app_info.data and len(app_info.data) > 0 else str(app_id)
        
        receipt_payload = {
            "version": "1.0",
            "consent_id": consent_id,
            "user_id": user_id,
            "app_id": str(app_id),  # Use resolved UUID
            "app_name": app_name,  # Include app name for readability
            "timestamp": datetime.utcnow().isoformat(),
            "expiry": expiry_time.isoformat(),
            "purposes": receipt_purposes
        }
        
        # 5. Sign Receipt
        signature = sign_payload(receipt_payload)
        
        # 6. Store Receipt
        db.table("consent_receipts").insert({
            "consent_id": consent_id,
            "signed_payload": receipt_payload,
            "signature": signature
        }).execute()
        
        # 7. Audit Log (Hash Chaining)
        # Fetch last event hash
        try:
            last_event = db.table("audit_events").select("hash_current").order("timestamp", desc=True).limit(1).execute()
            prev_hash = last_event.data[0]['hash_current'] if last_event.data and len(last_event.data) > 0 else "0" * 64
        except Exception as e:
            # If no events exist yet, start with zero hash
            prev_hash = "0" * 64
        
        current_hash = generate_hash_chain(prev_hash, receipt_payload, receipt_payload['timestamp'])
        
        audit_payload = {
            "event_type": "CONSENT_GRANTED",
            "actor_id": user_id,
            "actor_type": "USER",
            "event_payload": receipt_payload,
            "hash_prev": prev_hash,
            "hash_current": current_hash
        }
        
        db.table("audit_events").insert(audit_payload).execute()
        
        return ConsentReceiptResponse(
            receipt_id=str(uuid.uuid4()), # Just a placeholder, actual ID is in DB if needed
            consent_id=consent_id,
            receipt_payload=receipt_payload,
            signature=signature,
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like auth errors)
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in grant_consent: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/verify", response_model=VerificationResponse)
async def verify_receipt(request: VerifyReceiptRequest):
    """
    Verifies a consent receipt.
    Checks:
    1. Cryptographic signature.
    2. Expiry.
    3. Revocation status in DB.
    """
    payload = request.receipt
    
    # 1. Crypto Check (Stateless)
    # In a real scenario, the receipt should contain the signature or be passed alongside it.
    # For this prototype, we assume the receipt JSON passed *is* the signed payload structure? 
    # Wait, the verification usually needs the signature separate or embedded.
    # Let's assume the request has { "receipt": { ...payload... }, "signature": "..." } 
    # But our model VerifyReceiptRequest has `receipt: dict`.
    # Let's adjust logic: expect input to be the full object returned by grant?
    # Or simplified: The user provides the payload and the signature.
    # Let's say the Input is the `ConsentReceiptResponse` JSON essentially.
    
    # Attempt to extract signature if embedded, or fail.
    # Retrying logic: Let's assume the client sends the output of /grant.
    
    if "receipt_payload" not in payload or "signature" not in payload:
         return VerificationResponse(valid=False, status="invalid_format", message="Missing payload or signature")
         
    actual_payload = payload["receipt_payload"]
    signature = payload["signature"]
    
    if not verify_signature(actual_payload, signature):
        return VerificationResponse(valid=False, status="invalid_signature", message="Cryptographic verification failed")
        
    # 2. Expiry Check
    expiry_str = actual_payload.get("expiry")
    if expiry_str:
        expiry = datetime.fromisoformat(expiry_str)
        if datetime.utcnow() > expiry:
            return VerificationResponse(valid=False, status="expired", message="Consent has expired")
            
    # 3. Status Check (Revocation) - Stateful
    consent_id = actual_payload.get("consent_id")
    db = get_db()
    
    res = db.table("consents").select("status").eq("consent_id", consent_id).execute()
    if not res.data:
        return VerificationResponse(valid=False, status="unknown", message="Consent ID not found in ledger")
        
    status = res.data[0]['status']
    if status == 'revoked':
        return VerificationResponse(valid=False, status="revoked", message="Consent has been revoked by user")
        
    if status == 'expired': # redundancy
        return VerificationResponse(valid=False, status="expired", message="Consent marked expired in ledger")
        
    return VerificationResponse(valid=True, status="active", message="Consent is valid and active")

@router.post("/revoke")
async def revoke_consent(request: ConsentRevokeRequest, user = Depends(get_current_user)):
    """
    Revokes a consent.
    """
    db = get_db()
    
    # Update status
    res = db.table("consents").update({
        "status": "revoked",
        "revoked_at": datetime.utcnow().isoformat()
    }).eq("consent_id", request.consent_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Consent not found")
        
    # Audit Log
    # Fetch last event hash
    try:
        last_event = db.table("audit_events").select("hash_current").order("timestamp", desc=True).limit(1).execute()
        prev_hash = last_event.data[0]['hash_current'] if last_event.data and len(last_event.data) > 0 else "0" * 64
    except Exception as e:
        # If no events exist yet, start with zero hash
        prev_hash = "0" * 64
    
    event_payload = {
        "consent_id": request.consent_id,
        "action": "REVOKE",
        "reason": request.reason
    }
    
    timestamp = datetime.utcnow().isoformat()
    current_hash = generate_hash_chain(prev_hash, event_payload, timestamp)
    
    db.table("audit_events").insert({
        "event_type": "CONSENT_REVOKED",
        "actor_id": user.id if user else "system",
        "actor_type": "USER",
        "event_payload": event_payload,
        "timestamp": timestamp,
        "hash_prev": prev_hash,
        "hash_current": current_hash
    }).execute()
    
    return {"status": "revoked", "consent_id": request.consent_id}
