The Naukri.com Domain Support Agent capstone implementation has been completed end-to-end. All 12 building blocks across dataset design, RAG, multi-agent orchestration, guardrails, governance review, and deployment have been verified.
Architecture & System Overview
Deterministic Dataset Design: Generated 50 realistic job application records with fixed seed 42 distributed across 5 core job categories (Software Development, Product Management, Data Science, Quality Assurance, HR & Operations), tracking status stages, Indian Rupee compensation ranges, pipeline duration in days, and priority review flags.
Knowledge Base: Authored 12 official policy documents (KB-01 through KB-12) governing eligibility criteria, interview procedures, compensation brackets, notice periods, referral bonuses, internal job postings, probation guidelines, and applicant data retention.
RAG & Vector Retrieval:
Implemented two distinct chunking strategies: Fixed-Size with Overlap (180 character windows, 40 character sliding overlap) and Sentence-Based boundary chunking.
Built a 384-dimensional dense projection embedding engine with cosine similarity collection indexing.
Configured grounded generation with an empirically calibrated similarity cutoff threshold of 0.1800 to separate in-scope policy questions from out-of-scope inquiries.
Comparative Chunking Evaluation:
Executed a document-level precision and recall evaluation benchmark across canonical queries.
Results: Fixed-Size chunking achieved 80.0% Mean Precision and 100.0% Mean Recall, outperforming Sentence-Based chunking (46.7% Mean Precision, 100.0% Mean Recall) by preserving cross-sentence contextual continuity without diluting document focus.
Status Lookup & Escalation Engine:
Designed the candidate status tool calculating the composite escalation score: 
.
Calibrated the 80th-percentile alert threshold at 0.6400, automatically flagging high-priority bottlenecks (such as APP-1008) for immediate recruiter intervention.
Multi-Agent Crew Orchestration:
Intake & Privacy Guardian: Sanitizes queries, masks phone PII into [REDACTED_PHONE_NUMBER], and blocks adversarial prompt injections.
HR Policy Specialist: Executes grounded retrieval over official knowledge base documents.
Candidate Status Specialist: Looks up applicant records and evaluates pipeline urgency.
Lead Recruiter Orchestrator: Harmonizes intent routing (Policy FAQ, Application Status, Hybrid, or Refusal) and enforces the validated response schema.
Independent Compliance Review Team:
An independent governance panel reviews all drafted responses before delivery:
Legal & Statutory Compliance Officer (verifies compensation formatting, statutory guidelines, non-discrimination).
Data Privacy & Security Officer (asserts zero raw PII leakage and prompt injection refusal integrity).
Knowledge Groundedness Auditor (validates citations and factual alignment with source document chunks).
Emits an auditable compliance report with verdict status (APPROVED / REJECTED), compliance scoring, and detailed audit trail logs.
Production API & Interactive Interface:
Provides a standalone FastAPI backend (fastapi_app.py) for API deployment alongside an Express + Vite server (server.ts) hosting the interactive interface on port 3000.
Web Application Modules:
Agent Chat & Governance: Real-time conversation console with quick-test scenarios, structured schema inspection, and live compliance audit trails.
Candidate Applications Tracker: Interactive grid of all 50 deterministic records with filtering, searching, and visual breakdown of the escalation formula.
Knowledge Base Browser: Searchable viewer for all 12 official policy documents with department and version metadata.
Security & Guardrails Lab: Interactive sandbox for testing PII masking, jailbreak injections, and output hallucination filters.
RAG Benchmark Dashboard: Comparative evaluation view displaying per-query precision/recall arithmetic and deployment recommendations.
