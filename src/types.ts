export interface GuardrailStatus {
  pii_masked: boolean;
  masked_fields: string[];
  prompt_injection_detected: boolean;
  output_groundedness_passed: boolean;
}

export interface AgentResponseFormat {
  query: string;
  response_type: "policy_faq" | "application_status" | "hybrid" | "refusal";
  primary_doc_id: string | null;
  application_record_id: string | null;
  status: string | null;
  expected_salary_inr: number | null;
  escalation_score: number | null;
  escalation_recommended: boolean;
  draft_answer: string;
  grounded: boolean;
  guardrail_status: GuardrailStatus;
  citations: string[];
}

export interface ComplianceAudit {
  verdict: "APPROVED" | "REJECTED" | "FLAGGED_FOR_MODERATION";
  compliance_score: number;
  review_passed: boolean;
  audit_trail: string[];
  governance_notes: string;
  reviewers: string[];
}

export interface ChatResult {
  status: string;
  agent_response: AgentResponseFormat;
  compliance_audit: ComplianceAudit;
}

export interface JobApplication {
  record_id: string;
  category: string;
  status: string;
  expected_salary_inr: number;
  days_since_created: number;
  flagged_priority_review: boolean;
  escalation_score?: number;
  escalation_recommended?: boolean;
  rationale?: string;
}

export interface PolicyDocument {
  doc_id: string;
  topic: string;
  title: string;
  content: string;
  metadata: {
    category: string;
    department: string;
    version: string;
  };
}

export interface QueryEvaluationResult {
  query_id: string;
  query: string;
  ground_truth: string[];
  retrieved_parent_docs: string[];
  precision: number;
  recall: number;
  arithmetic_precision: string;
  arithmetic_recall: string;
}

export interface StrategyEvaluation {
  collection_name: string;
  chunk_count: number;
  query_results: QueryEvaluationResult[];
  mean_precision: number;
  mean_recall: number;
}

export interface ChunkingComparison {
  fixed_strategy: StrategyEvaluation;
  sentence_strategy: StrategyEvaluation;
  recommendation: string;
}
