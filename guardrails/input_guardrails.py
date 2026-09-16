"""
guardrails/input_guardrails.py - Input sanitization, PII masking, and injection filters.

Provides pre-flight protection for incoming user prompts:
- Redacts Indian and international mobile phone numbers to prevent privacy leakage
- Flags prompt injection attempts and system prompt extraction attacks
"""

import re
from typing import Any, Dict, List, Tuple

# Indian and international phone number pattern
PHONE_PATTERN = re.compile(
    r"(?:\+91[\s\-]?)?(?:[6-9]\d{4}[\s\-]?\d{5}|[6-9]\d{9}|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b)"
)

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(the\s+)?(system|all)\s+prompts?", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(security|guardrails|safety)", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?(secret|internal|system)\s+(prompt|instructions)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(dan|unrestricted|jailbroken|godmode)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"print\s+all\s+hidden\s+rules", re.IGNORECASE),
]


def mask_pii(text: str) -> Tuple[str, bool, List[str]]:
    """
    Masks fixed-format phone numbers in the input text.
    Returns (masked_text, pii_detected_bool, masked_fields_list).
    """
    masked_fields = []
    has_pii = False

    def replace_phone(match):
        nonlocal has_pii
        has_pii = True
        masked_fields.append("phone_number")
        return "[REDACTED_PHONE_NUMBER]"

    masked_text = PHONE_PATTERN.sub(replace_phone, text)
    return masked_text, has_pii, list(set(masked_fields))


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Detects adversarial prompt-injection attempts.
    Returns (is_injection, reason).
    """
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            return True, f"Adversarial instruction detected: '{match.group(0)}'"
    return False, ""


def apply_input_guardrails(raw_query: str) -> Dict[str, Any]:
    """
    Runs complete input guardrail pipeline:
    1. Mask fixed-format PII (phone number)
    2. Check for prompt injection
    """
    masked_query, has_pii, masked_fields = mask_pii(raw_query)
    is_injection, reason = detect_prompt_injection(masked_query)

    return {
        "raw_query": raw_query,
        "sanitized_query": masked_query,
        "pii_masked": has_pii,
        "masked_fields": masked_fields,
        "prompt_injection_detected": is_injection,
        "injection_reason": reason,
        "is_safe": not is_injection,
    }
