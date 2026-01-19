# How Regulators Detect Hash Chain Tampering

## Overview

The SAKSHAM system uses a **cryptographic hash chain** to create an immutable, tamper-evident audit log. This document explains how regulators can detect if the hash chain has been tampered with.

## What is a Hash Chain?

A hash chain is a sequence of events where each event's hash depends on:
1. The previous event's hash (`hash_prev`)
2. The current event's data (`event_payload`)
3. The event's timestamp

```
Event 1: hash_current = SHA256(prev_hash + payload1 + timestamp1)
Event 2: hash_current = SHA256(Event1.hash_current + payload2 + timestamp2)
Event 3: hash_current = SHA256(Event2.hash_current + payload3 + timestamp3)
...
```

**Key Property**: If ANY event is modified, deleted, or reordered, the hash chain breaks and tampering is detected.

## How Tampering is Detected

When a regulator clicks "Verify Hash Chain" in the Regulator Dashboard, the system performs three critical checks:

### Check 1: Data Integrity Verification

**What it checks**: Each event's `hash_current` matches the recalculated hash.

**How it works**:
1. For each event, the system recalculates the hash using:
   - The event's `hash_prev`
   - The event's `event_payload` (consent data)
   - The event's `timestamp`
2. Compares the recalculated hash with the stored `hash_current`
3. If they don't match → **TAMPERING DETECTED**

**What this detects**:
- ✅ Event data was modified (payload changed)
- ✅ Timestamp was altered
- ✅ Hash was manually changed

**Example Violation**:
```
Event ID: abc-123
Reason: Hash Mismatch - Event data may have been tampered with
Expected Hash: a1b2c3d4e5f6...
Found Hash: x9y8z7w6v5u4...
```

### Check 2: Chain Linkage Verification

**What it checks**: Each event's `hash_prev` matches the previous event's `hash_current`.

**How it works**:
1. Events are sorted chronologically (oldest first)
2. For each event (except the first), verify:
   - Event N's `hash_prev` == Event N-1's `hash_current`
3. If they don't match → **TAMPERING DETECTED**

**What this detects**:
- ✅ Events were deleted (chain link broken)
- ✅ Events were reordered (wrong previous hash)
- ✅ Events were inserted (invalid chain linkage)
- ✅ Events were modified in a way that breaks the chain

**Example Violation**:
```
Event ID: def-456
Reason: Chain Link Broken - Previous event hash mismatch
Expected Previous Hash: a1b2c3d4e5f6...
Found Previous Hash: m9n8o7p6q5r4...
Details: Possible deletion, reordering, or insertion detected
```

### Check 3: Duplicate Timestamp Detection

**What it checks**: No two events have the same timestamp.

**How it works**:
1. Collect all timestamps from events
2. Check for duplicates
3. If duplicates found → **SUSPICIOUS ACTIVITY**

**What this detects**:
- ✅ Unauthorized insertions (someone trying to insert events with same timestamp)
- ✅ Potential replay attacks
- ✅ System clock manipulation

## Verification Results

The regulator sees one of three statuses:

### ✅ VALID
- All checks passed
- No tampering detected
- Hash chain is intact

### ⚠️ TAMPERED
- Critical violations found
- Hash chain integrity compromised
- Immediate investigation required

### ⚠️ SUSPICIOUS
- Warnings detected (e.g., duplicate timestamps)
- May indicate attempted tampering
- Further investigation recommended

## Example: How Tampering is Detected

### Scenario 1: Event Data Modified

**Original Event**:
```json
{
  "event_id": "evt-123",
  "event_type": "CONSENT_GRANTED",
  "event_payload": {"consent_id": "c1", "user_id": "u1"},
  "hash_prev": "abc123...",
  "hash_current": "def456..."  // Calculated from above
}
```

**After Tampering** (someone changes user_id):
```json
{
  "event_id": "evt-123",
  "event_type": "CONSENT_GRANTED",
  "event_payload": {"consent_id": "c1", "user_id": "u2"},  // CHANGED!
  "hash_prev": "abc123...",
  "hash_current": "def456..."  // OLD HASH - NO LONGER VALID!
}
```

**Detection**: 
- Recalculated hash ≠ stored hash_current
- **Result**: TAMPERED - Hash Mismatch detected

### Scenario 2: Event Deleted

**Original Chain**:
```
Event 1: hash_current = "abc123"
Event 2: hash_prev = "abc123", hash_current = "def456"
Event 3: hash_prev = "def456", hash_current = "ghi789"
```

**After Deletion** (Event 2 removed):
```
Event 1: hash_current = "abc123"
Event 3: hash_prev = "def456"  // EXPECTS Event 2's hash, but Event 2 is gone!
```

**Detection**:
- Event 3's hash_prev doesn't match Event 1's hash_current
- **Result**: TAMPERED - Chain Link Broken

### Scenario 3: Event Reordered

**Original Order**:
```
Event A (10:00): hash_current = "aaa111"
Event B (10:05): hash_prev = "aaa111", hash_current = "bbb222"
Event C (10:10): hash_prev = "bbb222", hash_current = "ccc333"
```

**After Reordering** (B and C swapped):
```
Event A (10:00): hash_current = "aaa111"
Event C (10:10): hash_prev = "bbb222"  // WRONG! Should be "aaa111"
Event B (10:05): hash_prev = "aaa111"  // WRONG! Should be "ccc333"
```

**Detection**:
- Event C's hash_prev doesn't match Event A's hash_current
- **Result**: TAMPERED - Chain Link Broken

## Using the Regulator Dashboard

1. **Access Regulator View**:
   - Login to SAKSHAM
   - Select "Viewing as: Regulator" from dropdown

2. **View Audit Logs**:
   - See all consent events in chronological order
   - Each event shows its hash (first 16 characters)

3. **Verify Hash Chain**:
   - Click "Verify Hash Chain" button
   - System performs all three checks
   - Results displayed immediately

4. **Interpret Results**:
   - **VALID**: System is secure, no tampering
   - **TAMPERED**: Critical issue - investigate immediately
   - **SUSPICIOUS**: Review warnings, may need investigation

## Technical Details

### Hash Generation Formula

```python
hash_current = SHA256(
    hash_prev + 
    canonical_json(event_payload) + 
    timestamp
)
```

Where:
- `hash_prev`: Previous event's hash_current (or "0000..." for first event)
- `canonical_json()`: Deterministic JSON serialization (sorted keys, no whitespace)
- `timestamp`: ISO format timestamp string

### Why This Works

1. **Cryptographic Security**: SHA-256 is a one-way hash function
   - Cannot reverse-engineer original data from hash
   - Small change in input → completely different hash
   - Collision-resistant (extremely unlikely two inputs produce same hash)

2. **Chain Dependency**: Each hash depends on previous hash
   - Cannot modify one event without breaking the chain
   - Cannot delete events without breaking linkage
   - Cannot reorder events without breaking linkage

3. **Immutability**: Once written, events cannot be changed
   - Any modification is immediately detectable
   - Provides audit trail integrity

## Limitations & Considerations

### Current Implementation

- Verifies last N events (default: 100)
- For complete verification, all events from genesis must be checked
- Future enhancement: Full chain verification from beginning

### Performance

- Verification is O(n) where n = number of events
- For large audit logs, consider:
  - Incremental verification
  - Periodic full verification
  - Parallel processing

### False Positives

- System clock changes can cause timestamp issues
- Database migration might temporarily break chain
- Always investigate violations, but consider system changes

## Best Practices for Regulators

1. **Regular Verification**: Run hash chain verification periodically
2. **Document Violations**: Keep records of any tampering detected
3. **Investigate Immediately**: Critical violations require immediate action
4. **Compare with Backups**: If tampering detected, compare with backups
5. **Monitor Trends**: Track verification results over time

## Conclusion

The hash chain provides **cryptographic proof** of audit log integrity. Any tampering attempt is immediately detectable through:
- Hash mismatch (data modified)
- Chain breakage (events deleted/reordered)
- Anomaly detection (duplicate timestamps)

This gives regulators **confidence** that the audit trail is authentic and has not been tampered with, which is crucial for compliance and legal purposes.
