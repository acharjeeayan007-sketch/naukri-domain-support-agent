"""
agent/crew_agents.py - Multi-agent orchestration for recruitment support and governance.

Coordinates specialized pipeline workers:
- IntakeGuardrailAgent: Validates input integrity, scrubs phone PII, blocks adversarial injections
- PolicySpecialistAgent: Retrieves official HR policy knowledge with thresholded fallback
- CandidateStatusAgent: Resolves ATS application IDs and computes queue escalation scores
- LeadOrchestratorAgent: Synthesizes structured responses adhering to the enterprise schema
"""

from typing import Any, Dict, List, Optional
import re
from agent.schemas import AgentResponseFormat, GuardrailStatus
from guardrails.input_guardrails import apply_input_guardrails
from guardrails.output_guardrails import apply_output_guardrail
from rag.retrieval import generate_grounded_answer, SIMILARITY_THRESHOLD
from tools.status_lookup_tool import check_job_application_status, ESCALATION_THRESHOLD


class NaukriAgent:
    """Base class for domain service workers."""
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory


class IntakeGuardrailAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Input Privacy & Sanitization Guard",
            goal="Filter raw incoming queries for mobile PII and verify absence of prompt injection patterns.",
            backstory=(
                "Frontline ingress filter responsible for masking candidate phone numbers and catching "
                "adversarial prompt manipulation before queries enter internal business logic."
            ),
        )

    def process(self, query: str) -> Dict[str, Any]:
        return apply_input_guardrails(query)


class PolicySpecialistAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="HR Policy Retrieval Worker",
            goal="Execute semantic vector search against official recruitment policy documents with calibrated confidence.",
            backstory=(
                "Domain knowledge retrieval worker responsible for finding authoritative answers to questions "
                "regarding notice periods, eligibility criteria, referral schemes, and probation rules."
            ),
        )

    def answer_policy_query(self, query: str) -> Dict[str, Any]:
        return generate_grounded_answer(query)


class CandidateStatusAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Application Pipeline Worker",
            goal="Fetch candidate application records by ID and calculate recruiter queue escalation scores.",
            backstory=(
                "ATS interface worker that checks applicant stages, pipeline aging, and review priority flags."
            ),
        )

    def lookup_application(self, record_id: str) -> Dict[str, Any]:
        return check_job_application_status(record_id)


class LeadOrchestratorAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Talent Operations Orchestrator",
            goal="Route queries between status lookups and policy retrieval, synthesizing structured responses.",
            backstory=(
                "Central workflow dispatcher that coordinates workers and formats clean, audited output payloads."
            ),
        )

    def orchestrate(self, query: str) -> AgentResponseFormat:
        """
        Executes the sequential multi-agent pipeline:
          Step 1: Intake & Input Guardrail
          Step 2: Intent Classification & Routing (Policy vs Application Lookup vs Hybrid)
          Step 3: Specialist Task Execution
          Step 4: Output Guardrail & Verification
          Step 5: Schema Validation & Structured Output
        """
        # Step 1: Input Guardrail
        intake_res = IntakeGuardrailAgent().process(query)
        sanitized_query = intake_res["sanitized_query"]

        guardrail_diagnostics = GuardrailStatus(
            pii_masked=intake_res["pii_masked"],
            masked_fields=intake_res["masked_fields"],
            prompt_injection_detected=intake_res["prompt_injection_detected"],
            output_groundedness_passed=True,
        )

        # Handle adversarial prompt injection refusal immediately
        if intake_res["prompt_injection_detected"]:
            return AgentResponseFormat(
                query=query,
                response_type="refusal",
                primary_doc_id=None,
                application_record_id=None,
                status=None,
                expected_salary_inr=None,
                escalation_score=None,
                escalation_recommended=False,
                draft_answer=(
                    f"Security Notice: {intake_res['injection_reason']}. "
                    "Your request cannot be processed as it violates Naukri AI Security Governance policies."
                ),
                grounded=False,
                guardrail_status=guardrail_diagnostics,
                citations=[],
            )

        # Step 2: Extract potential Application ID (APP-XXXX)
        app_id_match = re.search(r"\bAPP-\d{4}\b", sanitized_query, re.IGNORECASE)
        app_record_id = app_id_match.group(0).upper() if app_id_match else None

        # Step 3: Route and execute specialist tasks
        status_res = None
        if app_record_id:
            status_res = CandidateStatusAgent().lookup_application(app_record_id)

        # Always check policy retrieval for content
        policy_res = PolicySpecialistAgent().answer_policy_query(sanitized_query)

        # Step 4: Synthesize response based on Intent
        if status_res and status_res.get("found"):
            # Application Status or Hybrid
            rec_id = status_res["record_id"]
            stat = status_res["status"]
            sal = status_res["expected_salary_inr"]
            cat = status_res["category"]
            days = status_res["days_since_created"]
            score = status_res["escalation_score"]
            escalate = status_res["escalation_recommended"]
            rationale = status_res["rationale"]

            formatted_salary = f"₹{sal:,.0f}" if sal else "N/A"
            escalation_badge = (
                f"⚠️ ESCALATION REQUIRED (Score: {score:.4f} >= {ESCALATION_THRESHOLD}): "
                "Application has been flagged for immediate recruiter intervention."
                if escalate
                else f"Status is normal (Escalation Score: {score:.4f} < {ESCALATION_THRESHOLD})."
            )

            status_msg = (
                f"Application Record [{rec_id}] for {cat}:\n"
                f"• Current Status: {stat}\n"
                f"• Expected Compensation: {formatted_salary} INR\n"
                f"• Days in Pipeline: {days} days\n"
                f"• Priority Review Flag: {status_res['flagged_priority_review']}\n"
                f"• Escalation Evaluation: {escalation_badge}\n"
                f"• Diagnostic Rationale: {rationale}"
            )

            # Check if user also asked a policy question in the same query (Hybrid)
            if policy_res["is_grounded"]:
                final_text = (
                    f"{status_msg}\n\n"
                    f"Relevant Policy Guidance:\n{policy_res['answer']}"
                )
                resp_type = "hybrid"
                citations = [rec_id, policy_res["primary_doc_id"]]
            else:
                final_text = status_msg
                resp_type = "application_status"
                citations = [rec_id]

            return AgentResponseFormat(
                query=query,
                response_type=resp_type,
                primary_doc_id=policy_res["primary_doc_id"] if policy_res["is_grounded"] else None,
                application_record_id=rec_id,
                status=stat,
                expected_salary_inr=sal,
                escalation_score=score,
                escalation_recommended=escalate,
                draft_answer=final_text,
                grounded=True,
                guardrail_status=guardrail_diagnostics,
                citations=citations,
            )

        elif app_record_id and not (status_res and status_res.get("found")):
            # Application lookup attempted but record not found
            return AgentResponseFormat(
                query=query,
                response_type="application_status",
                primary_doc_id=None,
                application_record_id=app_record_id,
                status=None,
                expected_salary_inr=None,
                escalation_score=None,
                escalation_recommended=False,
                draft_answer=(
                    f"Application record '{app_record_id}' could not be located in the Naukri talent database. "
                    "Please verify the 4-digit numeric code or contact your recruiter."
                ),
                grounded=False,
                guardrail_status=guardrail_diagnostics,
                citations=[],
            )

        # Policy FAQ flow
        if policy_res["is_grounded"]:
            # Apply Output Guardrail
            context_texts = [c["text"] for c in policy_res["retrieved_chunks"]]
            out_guard = apply_output_guardrail(policy_res["answer"], context_texts)
            guardrail_diagnostics.output_groundedness_passed = out_guard["passed"]

            return AgentResponseFormat(
                query=query,
                response_type="policy_faq",
                primary_doc_id=policy_res["primary_doc_id"],
                application_record_id=None,
                status=None,
                expected_salary_inr=None,
                escalation_score=None,
                escalation_recommended=False,
                draft_answer=out_guard["final_answer"],
                grounded=out_guard["passed"],
                guardrail_status=guardrail_diagnostics,
                citations=[policy_res["primary_doc_id"]],
            )
        else:
            # Fallback triggered
            return AgentResponseFormat(
                query=query,
                response_type="refusal",
                primary_doc_id=None,
                application_record_id=None,
                status=None,
                expected_salary_inr=None,
                escalation_score=None,
                escalation_recommended=False,
                draft_answer=policy_res["answer"],
                grounded=False,
                guardrail_status=guardrail_diagnostics,
                citations=[],
            )
