# Tampering Detection Demo Guide

This guide shows you how to demonstrate the hash chain tampering detection system.

## How to Demonstrate Tampering Detection

### Step 1: Verify Chain is Valid (Baseline)

1. Go to **Regulator Dashboard**
2. Click **"Verify Hash Chain"**
3. You should see: **Status: VALID** ✅
4. This confirms the chain is intact

### Step 2: Simulate Tampering

In the **Tampering Simulation** section:

1. **Select an Event**: Choose any event from the dropdown
2. Click one of the tampering buttons:

#### Option A: Simulate Hash Tampering
- **What it does**: Modifies the `hash_current` field to an obviously wrong value
- **What it detects**: Hash mismatch - the recalculated hash won't match the stored hash
- **Result**: "Hash Mismatch - Event data may have been tampered with"

#### Option B: Simulate Data Tampering
- **What it does**: Modifies the `event_payload` data (e.g., changes consent_id)
- **What it detects**: Hash mismatch - changing data changes the hash
- **Result**: "Hash Mismatch - Event data may have been tampered with"

#### Option C: Simulate Chain Break
- **What it does**: Breaks the chain by setting wrong `hash_prev`
- **What it detects**: Chain link broken - previous hash doesn't match
- **Result**: "Chain Link Broken - Previous event hash mismatch"

### Step 3: Verify Tampering is Detected

1. After simulating tampering, click **"Verify Hash Chain"** again
2. You should now see:
   - **Status: TAMPERED** ⚠️
   - **Critical Violation(s) Detected**
   - Detailed violation information showing:
     - Which event was tampered
     - What type of tampering was detected
     - Expected vs Found hash values

## Example Workflow

```
1. Initial State:
   ✅ Verify Hash Chain → Status: VALID

2. Simulate Tampering:
   - Select event: "CONSENT_GRANTED - 1/19/2026, 2:27:50 PM"
   - Click "Simulate Hash Tampering"
   - Message: "Hash Tampering simulated successfully!"

3. Detect Tampering:
   ✅ Verify Hash Chain → Status: TAMPERED
   ⚠️ 1 Critical Violation(s) Detected!
   [CRITICAL] Hash Mismatch - Event data may have been tampered with
```

## Types of Tampering You Can Simulate

### 1. Hash Tampering
**Simulates**: Someone manually changing the hash value
**Detection**: Hash mismatch on verification
**Real-world scenario**: Database administrator trying to hide changes

### 2. Data Tampering
**Simulates**: Someone modifying the actual event data
**Detection**: Hash mismatch (data change = different hash)
**Real-world scenario**: Malicious actor changing consent records

### 3. Chain Break
**Simulates**: Events being deleted or reordered
**Detection**: Chain link broken (hash_prev doesn't match)
**Real-world scenario**: Someone trying to remove audit trail entries

## Understanding the Results

### VALID Status
- ✅ All checks passed
- No tampering detected
- Chain is intact

### TAMPERED Status
- ⚠️ Critical violations found
- Hash chain integrity compromised
- Immediate investigation required

### Violation Details
Each violation shows:
- **Event ID**: Which event was tampered
- **Reason**: Type of tampering detected
- **Expected Hash**: What the hash should be
- **Found Hash**: What the hash actually is
- **Severity**: CRITICAL or WARNING

## Important Notes

⚠️ **These are DEMO endpoints only!**

- In production, these endpoints should **NOT exist**
- They're only for demonstrating tampering detection
- Real tampering would require direct database access
- The system is designed to detect tampering, not prevent it

## Real-World Tampering Scenarios

### Scenario 1: Malicious Database Admin
- Admin tries to modify consent records
- Changes event data in database
- **Detection**: Hash mismatch on next verification

### Scenario 2: Data Breach
- Attacker modifies audit logs
- Tries to cover tracks by changing hashes
- **Detection**: Hash mismatch + chain break

### Scenario 3: System Compromise
- Malware modifies database records
- Changes multiple events
- **Detection**: Multiple violations detected

## Best Practices for Demonstrations

1. **Start with Valid Chain**: Always verify chain is valid first
2. **Simulate One Type**: Try one tampering type at a time
3. **Show Detection**: Immediately verify after tampering
4. **Explain Results**: Walk through what each violation means
5. **Reset if Needed**: Create new events if you want to test again

## Technical Details

### How Detection Works

1. **Hash Recalculation**: System recalculates hash from stored data
2. **Comparison**: Compares recalculated hash with stored hash
3. **Chain Verification**: Checks each event links to previous event
4. **Anomaly Detection**: Looks for duplicate timestamps, gaps, etc.

### Hash Calculation Formula

```
hash_current = SHA256(
    hash_prev + 
    canonical_json(event_payload) + 
    timestamp
)
```

Any change to:
- Previous hash → Chain breaks
- Event payload → Hash changes
- Timestamp → Hash changes

## Conclusion

The tampering simulation demonstrates that:
- ✅ Any modification is immediately detectable
- ✅ The system provides cryptographic proof of tampering
- ✅ Regulators can verify audit log integrity independently
- ✅ The system is tamper-evident, not tamper-proof

This gives regulators confidence that audit logs are authentic and can be trusted for compliance and legal purposes.
