"""
fastapi_app.py - Production-Grade FastAPI Backend for Naukri.com Domain Support Agent.
Track: Recruitment & HR (Naukri.com) - Capstone Part 3 Task 12.

Features:
  - Pydantic request & response validation
  - Structured API response adhering to AgentResponseFormat
  - Endpoints for Chat, Status Lookups, Policy KB, Guardrails, and RAG Evaluation
  - Independent Compliance Review Audit on all user-bound responses
"""

from typing import Any, Dict, List, Optional
import os
import sys

# Core Agent Imports
from agent.crew_agents import LeadOrchestratorAgent
from agent.compliance_review import IndependentComplianceReviewTeam
from dataset import JOB_APPLICATIONS
from knowledge_base.documents import KNOWLEDGE_BASE_DOCS, KNOWLEDGE_BASE_DOCS_BY_ID
from tools.status_lookup_tool import check_job_application_status
from guardrails.input_guardrails import apply_input_guardrails
from guardrails.output_guardrails import apply_output_guardrail
from rag.evaluation import compare_chunking_strategies

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object
    Field = lambda *args, **kwargs: None


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Naukri.com Domain Support Agent API",
        description="Production API with CrewAI Orchestration, Guardrails, and Compliance Review",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    orchestrator = LeadOrchestratorAgent()
    compliance_team = IndependentComplianceReviewTeam()

    class ChatRequest(BaseModel):
        query: str = Field(..., description="Candidate or recruiter inquiry text", example="What is the notice period policy?")

    class GuardrailInputRequest(BaseModel):
        text: str = Field(..., description="Raw text to test against input guardrails")

    class GuardrailOutputRequest(BaseModel):
        answer: str = Field(..., description="Draft answer to verify")
        context_chunks: List[str] = Field(default_factory=list, description="Retrieved context chunks")

    @app.get("/health", tags=["System"])
    def health_check():
        return {
            "status": "healthy",
            "service": "Naukri Domain Support Agent",
            "version": "1.0.0",
            "offline_mode": True,
            "kb_documents_loaded": len(KNOWLEDGE_BASE_DOCS),
            "application_records_loaded": len(JOB_APPLICATIONS),
        }

    @app.post("/chat", tags=["Agent"])
    def chat_endpoint(req: ChatRequest):
        """
        Executes the Crew multi-agent orchestration pipeline with independent compliance review.
        """
        if not req.query or not req.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        agent_resp = orchestrator.orchestrate(req.query.strip())
        audit_res = compliance_team.audit(agent_resp)

        return {
            "agent_response": agent_resp.dict(),
            "compliance_audit": audit_res,
        }

    @app.get("/applications", tags=["Recruitment Data"])
    def get_applications(
        category: Optional[str] = None,
        status: Optional[str] = None,
        escalation_only: bool = False,
        search: Optional[str] = None,
    ):
        """Retrieves and filters candidate application records with escalation metrics."""
        results = []
        for app_rec in JOB_APPLICATIONS:
            rec_id = app_rec["record_id"]
            evaluated = check_job_application_status(rec_id)
            
            # Apply filters
            if category and app_rec["category"].lower() != category.lower():
                continue
            if status and app_rec["status"].lower() != status.lower():
                continue
            if escalation_only and not evaluated["escalation_recommended"]:
                continue
            if search:
                search_lower = search.lower()
                matches_id = search_lower in rec_id.lower()
                matches_cat = search_lower in app_rec["category"].lower()
                matches_stat = search_lower in app_rec["status"].lower()
                if not (matches_id or matches_cat or matches_stat):
                    continue

            results.append({
                **app_rec,
                "escalation_score": evaluated["escalation_score"],
                "escalation_recommended": evaluated["escalation_recommended"],
                "rationale": evaluated["rationale"],
            })

        return {
            "total_matches": len(results),
            "total_dataset_size": len(JOB_APPLICATIONS),
            "applications": results,
        }

    @app.get("/applications/{record_id}", tags=["Recruitment Data"])
    def get_application_by_id(record_id: str):
        res = check_job_application_status(record_id.upper())
        if not res["found"]:
            raise HTTPException(status_code=404, detail=f"Application record '{record_id}' not found.")
        return res

    @app.get("/policies", tags=["Knowledge Base"])
    def get_policies():
        return {
            "total": len(KNOWLEDGE_BASE_DOCS),
            "policies": KNOWLEDGE_BASE_DOCS,
        }

    @app.get("/policies/{doc_id}", tags=["Knowledge Base"])
    def get_policy_by_id(doc_id: str):
        doc = KNOWLEDGE_BASE_DOCS_BY_ID.get(doc_id.upper())
        if not doc:
            raise HTTPException(status_code=404, detail=f"Policy document '{doc_id}' not found.")
        return doc

    @app.post("/guardrails/input", tags=["Security & Guardrails"])
    def test_input_guardrail(req: GuardrailInputRequest):
        return apply_input_guardrails(req.text)

    @app.post("/guardrails/output", tags=["Security & Guardrails"])
    def test_output_guardrail(req: GuardrailOutputRequest):
        return apply_output_guardrail(req.answer, req.context_chunks)

    @app.get("/evaluation", tags=["RAG Evaluation"])
    def get_rag_evaluation():
        """Returns comparative evaluation metrics for Fixed vs Sentence chunking."""
        return compare_chunking_strategies()

else:
    # Lightweight standard library HTTP server fallback when fastapi/uvicorn is not in python path
    import http.server
    import json
    from urllib.parse import urlparse, parse_qs

    orchestrator = LeadOrchestratorAgent()
    compliance_team = IndependentComplianceReviewTeam()

    class NaukriHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
        def _send_json(self, data: Any, status: int = 200):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path

            if path in ("/health", "/api/health"):
                self._send_json({
                    "status": "healthy",
                    "service": "Naukri Domain Support Agent",
                    "version": "1.0.0",
                    "offline_mode": True,
                    "kb_documents_loaded": len(KNOWLEDGE_BASE_DOCS),
                    "application_records_loaded": len(JOB_APPLICATIONS),
                })
            elif path in ("/policies", "/api/policies"):
                self._send_json({"total": len(KNOWLEDGE_BASE_DOCS), "policies": KNOWLEDGE_BASE_DOCS})
            elif path in ("/applications", "/api/applications"):
                evaluated_apps = []
                for a in JOB_APPLICATIONS:
                    ev = check_job_application_status(a["record_id"])
                    evaluated_apps.append({
                        **a,
                        "escalation_score": ev["escalation_score"],
                        "escalation_recommended": ev["escalation_recommended"],
                        "rationale": ev["rationale"],
                    })
                self._send_json({"total": len(evaluated_apps), "applications": evaluated_apps})
            elif path in ("/evaluation", "/api/evaluation"):
                self._send_json(compare_chunking_strategies())
            else:
                self._send_json({"error": "Endpoint not found"}, status=404)

        def do_POST(self):
            parsed = urlparse(self.path)
            length = int(self.headers.get("content-length", 0))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                data = json.loads(raw_body)
            except Exception:
                data = {}

            if parsed.path in ("/chat", "/api/chat"):
                query = data.get("query", "").strip()
                if not query:
                    self._send_json({"error": "Query cannot be empty"}, status=400)
                    return
                resp = orchestrator.orchestrate(query)
                audit = compliance_team.audit(resp)
                self._send_json({
                    "agent_response": resp.dict(),
                    "compliance_audit": audit,
                })
            elif parsed.path in ("/guardrails/input", "/api/guardrails/input"):
                text = data.get("text", "")
                self._send_json(apply_input_guardrails(text))
            elif parsed.path in ("/guardrails/output", "/api/guardrails/output"):
                ans = data.get("answer", "")
                ctx = data.get("context_chunks", [])
                self._send_json(apply_output_guardrail(ans, ctx))
            else:
                self._send_json({"error": "Endpoint not found"}, status=404)


def run_standalone(port: int = 8000):
    if FASTAPI_AVAILABLE:
        import uvicorn
        print(f"Starting FastAPI server on http://0.0.0.0:{port}...")
        uvicorn.run("fastapi_app:app", host="0.0.0.0", port=port, reload=False)
    else:
        print(f"FastAPI not detected; starting built-in HTTP server on http://0.0.0.0:{port}...")
        server = http.server.HTTPServer(("0.0.0.0", port), NaukriHTTPRequestHandler)
        server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_standalone(port)
