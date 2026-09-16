"""
agent_bridge.py - Standard JSON CLI Bridge for Naukri Domain Support Agent.
Enables Node.js / Express or any external client to invoke the Python multi-agent system,
knowledge retrieval, application lookups, guardrails, and compliance audits seamlessly.
"""

import sys
import json
from agent.crew_agents import LeadOrchestratorAgent
from agent.compliance_review import IndependentComplianceReviewTeam
from dataset import JOB_APPLICATIONS
from knowledge_base.documents import KNOWLEDGE_BASE_DOCS
from tools.status_lookup_tool import check_job_application_status
from guardrails.input_guardrails import apply_input_guardrails
from guardrails.output_guardrails import apply_output_guardrail
from rag.retrieval import generate_grounded_answer
from rag.evaluation import run_evaluation_suite


_ORCHESTRATOR = None
_COMPLIANCE_TEAM = None


def get_orchestrator():
    global _ORCHESTRATOR
    if _ORCHESTRATOR is None:
        _ORCHESTRATOR = LeadOrchestratorAgent()
    return _ORCHESTRATOR


def get_compliance_team():
    global _COMPLIANCE_TEAM
    if _COMPLIANCE_TEAM is None:
        _COMPLIANCE_TEAM = IndependentComplianceReviewTeam()
    return _COMPLIANCE_TEAM


def handle_request(payload: dict) -> dict:
    action = payload.get("action", "chat")

    if action == "chat":
        query = payload.get("query", "").strip()
        if not query:
            return {"error": "Query cannot be empty"}
        
        orch = get_orchestrator()
        team = get_compliance_team()
        
        agent_resp = orch.orchestrate(query)
        audit_res = team.audit(agent_resp)
        
        return {
            "status": "success",
            "agent_response": agent_resp.dict(),
            "compliance_audit": audit_res,
        }

    elif action == "lookup":
        record_id = payload.get("record_id", "").strip().upper()
        res = check_job_application_status(record_id)
        return {"status": "success", "result": res}

    elif action == "dataset":
        return {"status": "success", "total": len(JOB_APPLICATIONS), "records": JOB_APPLICATIONS}

    elif action == "policies":
        return {"status": "success", "total": len(KNOWLEDGE_BASE_DOCS), "policies": KNOWLEDGE_BASE_DOCS}

    elif action == "test_guardrail":
        text = payload.get("text", "")
        mode = payload.get("mode", "input")
        if mode == "input":
            res = apply_input_guardrails(text)
            return {"status": "success", "result": res}
        else:
            context = payload.get("context", [])
            res = apply_output_guardrail(text, context)
            return {"status": "success", "result": res}

    elif action == "evaluate":
        res = run_evaluation_suite()
        return {"status": "success", "evaluation": res}

    else:
        return {"error": f"Unknown action: {action}"}


def main():
    if len(sys.argv) > 1:
        # Argument mode
        input_data = sys.argv[1]
        try:
            payload = json.loads(input_data)
        except Exception:
            payload = {"action": "chat", "query": input_data}
    else:
        # Stdin mode
        raw = sys.stdin.read().strip()
        if not raw:
            print(json.dumps({"error": "Empty stdin payload"}))
            return
        payload = json.loads(raw)

    response = handle_request(payload)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
