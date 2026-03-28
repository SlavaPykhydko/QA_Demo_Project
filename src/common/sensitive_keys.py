"""Centralized sensitive-key definitions used for logging and report masking."""

# Keep keys in lowercase for case-insensitive comparisons.
SENSITIVE_KEYS = {
    "authorization",
    "x-api-key",
    "x-fuser-id",
    "token",
    "access_token",
    "refresh_token",
    "password",
    "session_id",
    "cookie",
}

