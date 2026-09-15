"""
agent/crew_agents.py - Multi-Agent Crew Definitions for Naukri.com Domain Support.
Track: Recruitment & HR (Naukri.com) - Capstone Part 2 Tasks 7 & 8.

Defines 4 specialized agents:
  1. Intake & Guardrail Agent: Sanitizes inputs, masks phone PII, blocks adversarial injections.
  2. HR Policy Specialist Agent: Grounded retrieval over official Naukri knowledge base policies.
  3. Candidate Status Specialist Agent: Application lookup & escalation scoring (threshold 0.6400).
  4. Lead Recruiter Orchestrator Agent: Synthesizes final response adhering to AgentResponseFormat.
"""

from typing import Any, Dict, List, Optional
import re
from agent.schemas import AgentResponseFormat, GuardrailStatus
from guardrails.input_guardrails import apply_input_guardrails
from guardrails.output_guardrails import apply_output_guardrail
from rag.retrieval import generate_grounded_answer, SIMILARITY_THRESHOLD
from tools.status_lookup_tool import check_job_application_status, ESCALATION_THRESHOLD


class NaukriAgent:
    """Base class for domain agents."""
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory


class IntakeGuardrailAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Recruitment Intake & Privacy Guardian",
            goal="Ensure all incoming user messages are scrubbed of phone PII and vetted against prompt-injection attacks.",
            backstory=(
                "You are the frontline security specialist for Naukri.com. You inspect all candidate and recruiter "
                "inquiries to redact sensitive phone numbers and neutralize adversarial instruction injections."
            ),
        )

    def process(self, query: str) -> Dict[str, Any]:
        return apply_input_guardrails(query)


class PolicySpecialistAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="HR Policy Knowledge Specialist",
            goal="Provide factual, strictly grounded answers regarding official Naukri recruitment and HR policies.",
            backstory=(
                "You are a certified Naukri.com People Operations partner with exhaustive knowledge of company "
                "policies covering eligibility, notice periods, referral bonuses, internal transfers, and offboarding."
            ),
        )

    def answer_policy_query(self, query: str) -> Dict[str, Any]:
        return generate_grounded_answer(query)


class CandidateStatusAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Candidate Application & Escalation Specialist",
            goal="Accurately look up candidate applications and evaluate escalation urgency using the calibrated composite score.",
            backstory=(
                "You manage the talent acquisition pipeline for Naukri.com. You monitor application progression, "
                "benchmark salaries, track days pending, and flag critical bottlenecks for immediate recruiter escalation."
            ),
        )

    def lookup_application(self, record_id: str) -> Dict[str, Any]:
        return check_job_application_status(record_id)


class LeadOrchestratorAgent(NaukriAgent):
    def __init__(self):
        super().__init__(
            role="Lead Talent Operations Orchestrator",
            goal="Coordinate multi-agent workflows, synthesize specialist outputs, and enforce the AgentResponseFormat schema.",
            backstory=(
                "You oversee end-to-end recruitment support for Naukri.com. You harmonize policy retrieval and "
                "application tracking into professional, compliant, and actionable communications."
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
