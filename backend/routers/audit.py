from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from database import get_db
from routers.auth import get_current_user, require_role

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/events")
async def get_audit_events(
    limit: int = 50, 
    user_id: Optional[str] = None, 
    user = Depends(get_current_user)
):
    """
    Retrieve audit events. 
    In a real system, this would be restricted to Regulators or App Admins.
    """
    db = get_db()
    query = db.table("audit_events").select("*").order("timestamp", desc=True).limit(limit)
    
    if user_id:
        query = query.eq("actor_id", user_id)
        
    res = query.execute()
    return res.data

@router.get("/verify-chain")
async def verify_hash_chain(limit: int = 100):
    """
    Utility for regulators to verify the integrity of the hash chain.
    Fetches the last N events and re-computes hashes to ensure no tampering.
    
    Verification checks:
    1. Each event's hash_current matches recalculated hash (data integrity)
    2. Each event's hash_prev matches previous event's hash_current (chain linkage)
    3. No gaps or breaks in the chain
    """
    db = get_db()
    # Get events ordered by timestamp (oldest first) for proper chain verification
    res = db.table("audit_events").select("*").order("timestamp", desc=False).limit(limit).execute()
    events = res.data
    
    if not events or len(events) == 0:
        return {
            "verified_count": 0,
            "violations": [],
            "status": "EMPTY",
            "message": "No audit events found"
        }
    
    violations = []
    from utils import generate_hash_chain
    
    # Sort events by timestamp to verify chain in chronological order
    sorted_events = sorted(events, key=lambda x: x['timestamp'])
    
    # Start with the first event (genesis or earliest in batch)
    prev_hash_expected = sorted_events[0].get('hash_prev', "0" * 64)
    
    for i, event in enumerate(sorted_events):
        event_id = event['event_id']
        event_timestamp = event['timestamp']
        event_type = event['event_type']
        event_payload = event['event_payload']
        
        # IMPORTANT: Use timestamp from event_payload if available
        # The hash was originally calculated using receipt_payload['timestamp'] (ISO string)
        # not the database timestamp column
        hash_timestamp = None
        if isinstance(event_payload, dict):
            hash_timestamp = event_payload.get('timestamp')
            # Ensure it's a string (JSONB might return it in different format)
            if hash_timestamp and not isinstance(hash_timestamp, str):
                if hasattr(hash_timestamp, 'isoformat'):
                    hash_timestamp = hash_timestamp.isoformat()
                else:
                    hash_timestamp = str(hash_timestamp)
        
        # Fallback: convert database timestamp to ISO string format (for REVOKE events that don't have timestamp in payload)
        if not hash_timestamp:
            if isinstance(event_timestamp, str):
                hash_timestamp = event_timestamp
            else:
                # If it's a datetime object, convert to ISO string
                from datetime import datetime
                if hasattr(event_timestamp, 'isoformat'):
                    hash_timestamp = event_timestamp.isoformat()
                else:
                    hash_timestamp = str(event_timestamp)
        
        # Check 1: Verify hash_current matches recalculated hash
        # This detects if the event data was modified
        # Use the same timestamp that was used when creating the hash
        recalc_hash = generate_hash_chain(
            event['hash_prev'], 
            event_payload, 
            hash_timestamp
        )
        
        # Debug: Log hash calculation details if mismatch
        if recalc_hash != event['hash_current']:
            import json
            print(f"DEBUG: Hash mismatch for event {event_id}")
            print(f"  hash_prev: {event['hash_prev']}")
            print(f"  timestamp used: {hash_timestamp}")
            print(f"  event_payload type: {type(event_payload)}")
            print(f"  event_payload keys: {list(event_payload.keys()) if isinstance(event_payload, dict) else 'N/A'}")
            print(f"  event_payload JSON: {json.dumps(event_payload, sort_keys=True)}")
            print(f"  expected hash: {recalc_hash}")
            print(f"  stored hash: {event['hash_current']}")
        
        if recalc_hash != event['hash_current']:
            violations.append({
                "event_id": str(event_id),
                "event_type": event_type,
                "timestamp": event_timestamp,
                "reason": "Hash Mismatch - Event data may have been tampered with",
                "details": f"Recalculated hash doesn't match stored hash_current",
                "expected_hash": recalc_hash,
                "found_hash": event['hash_current'],
                "severity": "CRITICAL"
            })
        
        # Check 2: Verify chain linkage (hash_prev matches previous event's hash_current)
        # This detects if events were deleted, reordered, or inserted
        if i > 0:  # First event doesn't have a previous event in this batch
            if event['hash_prev'] != prev_hash_expected:
                violations.append({
                    "event_id": str(event_id),
                    "event_type": event_type,
                    "timestamp": event_timestamp,
                    "reason": "Chain Link Broken - Previous event hash mismatch",
                    "details": f"Event's hash_prev doesn't match previous event's hash_current. Possible deletion, reordering, or insertion.",
                    "expected_prev_hash": prev_hash_expected,
                    "found_prev_hash": event['hash_prev'],
                    "severity": "CRITICAL"
                })
        
        # Update expected previous hash for next iteration
        prev_hash_expected = event['hash_current']
    
    # Check 3: Verify no duplicate timestamps (potential insertion attack)
    timestamps = [e['timestamp'] for e in sorted_events]
    if len(timestamps) != len(set(timestamps)):
        violations.append({
            "event_id": "MULTIPLE",
            "reason": "Duplicate Timestamps Detected",
            "details": "Multiple events have the same timestamp. This may indicate unauthorized insertions.",
            "severity": "WARNING"
        })
    
    # Determine overall status
    critical_violations = [v for v in violations if v.get('severity') == 'CRITICAL']
    status = "VALID" if not violations else ("TAMPERED" if critical_violations else "SUSPICIOUS")
    
    return {
        "verified_count": len(events),
        "total_events": len(events),
        "violations": violations,
        "critical_violations": len(critical_violations),
        "warnings": len([v for v in violations if v.get('severity') == 'WARNING']),
        "status": status,
        "message": "Chain verified successfully" if status == "VALID" else f"Found {len(violations)} violation(s)"
    }

@router.post("/tamper")
async def tamper_log(user = Depends(get_current_user)):
    """
    SIMULATION ONLY: Corrupts the last audit event to demonstrate the verification engine.
    This modifies the 'hash_current' of the most recent event in the DB, breaking the chain.
    """
    db = get_db()
    # Get last event
    last_event = db.table("audit_events").select("event_id").order("timestamp", desc=True).limit(1).execute()
    if not last_event.data:
        raise HTTPException(status_code=404, detail="No events to tamper with")
        
    event_id = last_event.data[0]['event_id']
    
    # Corrupt it efficiently
    db.table("audit_events").update({
        "hash_current": "DEADBEEF00000000000000000000000000000000000000000000000000000000"
    }).eq("event_id", event_id).execute()
    
    return {"status": "tampered", "message": "The ledger has been corrupted. Run verification to detect."}

@router.post("/simulate-tamper/{event_id}")
async def simulate_tampering(event_id: str, user = Depends(get_current_user)):
    """
    DEMO ONLY: Simulates tampering by modifying an event's hash.
    This is for demonstration purposes to show how tampering detection works.
    In production, this endpoint should NOT exist.
    """
    db = get_db()
    
    # Get the event
    res = db.table("audit_events").select("*").eq("event_id", event_id).execute()
    if not res.data or len(res.data) == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = res.data[0]
    
    # Simulate tampering by modifying the hash_current
    # This creates a hash mismatch that will be detected
    tampered_hash = "0" * 64  # Obviously wrong hash
    
    # Update the event with tampered hash
    db.table("audit_events").update({
        "hash_current": tampered_hash
    }).eq("event_id", event_id).execute()
    
    return {
        "message": "Tampering simulated successfully",
        "event_id": event_id,
        "original_hash": event['hash_current'],
        "tampered_hash": tampered_hash,
        "note": "Run 'Verify Hash Chain' to see the tampering detection"
    }

@router.post("/simulate-tamper-data/{event_id}")
async def simulate_data_tampering(event_id: str, user = Depends(get_current_user)):
    """
    DEMO ONLY: Simulates tampering by modifying event payload data.
    This changes the actual data, which will cause hash mismatch.
    """
    db = get_db()
    
    # Get the event
    res = db.table("audit_events").select("*").eq("event_id", event_id).execute()
    if not res.data or len(res.data) == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = res.data[0]
    event_payload = event['event_payload']
    
    # Modify the payload (simulate data tampering)
    if isinstance(event_payload, dict):
        # Add a tampered field or modify existing data
        if 'consent_id' in event_payload:
            event_payload['consent_id'] = "TAMPERED-" + event_payload.get('consent_id', '')
        elif 'action' in event_payload:
            event_payload['action'] = "TAMPERED_" + event_payload.get('action', '')
    
    # Update the event with tampered payload
    db.table("audit_events").update({
        "event_payload": event_payload
    }).eq("event_id", event_id).execute()
    
    return {
        "message": "Data tampering simulated successfully",
        "event_id": event_id,
        "tampered_payload": event_payload,
        "note": "Run 'Verify Hash Chain' to see the tampering detection"
    }

@router.post("/simulate-tamper-chain/{event_id}")
async def simulate_chain_tampering(event_id: str, user = Depends(get_current_user)):
    """
    DEMO ONLY: Simulates chain tampering by breaking the hash_prev link.
    This simulates deletion or reordering of events.
    """
    db = get_db()
    
    # Get the event
    res = db.table("audit_events").select("*").eq("event_id", event_id).execute()
    if not res.data or len(res.data) == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = res.data[0]
    
    # Break the chain by setting wrong hash_prev
    broken_hash_prev = "BROKEN_CHAIN_" + "0" * 50
    
    # Update the event with broken chain link
    db.table("audit_events").update({
        "hash_prev": broken_hash_prev
    }).eq("event_id", event_id).execute()
    
    return {
        "message": "Chain tampering simulated successfully",
        "event_id": event_id,
        "original_hash_prev": event['hash_prev'],
        "broken_hash_prev": broken_hash_prev,
        "note": "Run 'Verify Hash Chain' to see the chain link breakage detection"
    }
