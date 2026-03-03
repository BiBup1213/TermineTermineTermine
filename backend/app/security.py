import hashlib
import hmac
import os
import secrets

TOKEN_PEPPER = os.getenv("TOKEN_PEPPER", "dev-pepper-change-me")


def generate_token() -> str:
    return secrets.token_urlsafe(24)


def hash_token(raw_token: str) -> str:
    payload = f"{TOKEN_PEPPER}:{raw_token}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_token(raw_token: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_token(raw_token), expected_hash)
