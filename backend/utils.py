import json
import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# --- GLOBAL KEY MOCK (simulating a private PKI for the Consent Manager) ---
# In production, this would be loaded from a secure vault.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

def get_public_key_pem():
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

def canonical_json(payload: dict) -> bytes:
    """
    Produces a deterministic JSON byte string.
    Keys are sorted, no whitespace.
    """
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sign_payload(payload: dict) -> str:
    """
    Signs the canonical JSON of the payload using the system's private key.
    Returns Base64 encoded signature.
    """
    data = canonical_json(payload)
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(payload: dict, signature_b64: str) -> bool:
    """
    Verifies that the payload matches the signature.
    """
    try:
        data = canonical_json(payload)
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def generate_hash_chain(prev_hash: str, current_payload: dict, timestamp: str) -> str:
    """
    Generates a SHA-256 hash for the current event, linking it to the previous one.
    Hash = SHA256(prev_hash + canonical_payload + timestamp)
    """
    content = (prev_hash or "") + json.dumps(current_payload, sort_keys=True) + timestamp
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
