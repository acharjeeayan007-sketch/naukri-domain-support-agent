"""
agent/schemas.py - Structured Output Schema for Crew Responses.
Track: Recruitment & HR (Naukri.com) - Capstone Part 2 Task 9.

Defines Pydantic BaseModel (AgentResponseFormat) validated on every response.
"""

from typing import Any, Dict, List, Optional
import json

try:
    from pydantic import BaseModel, Field
except ImportError:
    from dataclasses import dataclass, field, asdict

    def Field(default=None, default_factory=None, description=None):
        if default_factory is not None:
            return field(default_factory=default_factory)
        return field(default=default)

    class BaseModel:
        def dict(self) -> Dict[str, Any]:
            return asdict(self)

        def model_dump(self) -> Dict[str, Any]:
            return asdict(self)

        def json(self) -> str:
            return json.dumps(self.dict())


@dataclass if "dataclass" in globals() else lambda cls: cls
class GuardrailStatus(BaseModel):
    pii_masked: bool = Field(default=False, description="True if fixed-format PII (phone) was detected & masked")
    masked_fields: List[str] = Field(default_factory=list, description="Names of masked fields")
    prompt_injection_detected: bool = Field(default=False, description="True if prompt injection was caught")
    output_groundedness_passed: bool = Field(default=True, description="True if answer is supported by context")


@dataclass if "dataclass" in globals() else lambda cls: cls
class AgentResponseFormat(BaseModel):
    """Canonical structured response model returned by the agent orchestration layer."""
    query: str = Field(description="Original or sanitized user query")
    response_type: str = Field(description="Type of response: 'policy_faq', 'application_status', 'hybrid', 'refusal'")
    primary_doc_id: Optional[str] = Field(default=None, description="Primary Knowledge Base document ID if policy-based")
    application_record_id: Optional[str] = Field(default=None, description="Job application record ID if status lookup")
    status: Optional[str] = Field(default=None, description="Candidate application status")
    expected_salary_inr: Optional[int] = Field(default=None, description="Candidate expected salary in INR")
    escalation_score: Optional[float] = Field(default=None, description="Composite escalation score in [0.0, 1.0]")
    escalation_recommended: Optional[bool] = Field(default=False, description="True if score >= 80th percentile threshold (0.64)")
    draft_answer: str = Field(default="", description="Composed final response text")
    grounded: bool = Field(default=True, description="True if response is grounded in retrieved context or DB")
    guardrail_status: GuardrailStatus = Field(default_factory=GuardrailStatus, description="Diagnostics from input/output guardrails")
    citations: List[str] = Field(default_factory=list, description="Referenced document IDs or records")
