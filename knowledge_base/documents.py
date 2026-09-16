"""
knowledge_base/documents.py - Official HR and recruitment policy provisions.

Canonical knowledge base documents queried by the RAG retrieval pipeline:
Covers candidate eligibility, scheduling SLA, notice period guidelines,
probation rules, internal mobility (IJP), referral bonuses, and compliance standards.
"""

from typing import Any, Dict, List

KNOWLEDGE_BASE_DOCS: List[Dict[str, Any]] = [
    {
        "doc_id": "KB-01",
        "topic": "job-application eligibility criteria",
        "title": "Job Application Eligibility Criteria",
        "content": (
            "Candidates must hold an accredited Bachelor's degree or equivalent professional diploma "
            "relevant to the target job family before submitting an application. A minimum cumulative "
            "academic score of sixty percent or equivalent CGPA is required across all formal qualifications. "
            "Applicants must also possess legal work authorization for India or have active eligibility for employer sponsorship. "
            "Any submission with falsified academic records or unverified employment credentials will result in immediate disqualification."
        ),
        "metadata": {
            "category": "eligibility",
            "department": "Talent Acquisition",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-02",
        "topic": "interview-scheduling process",
        "title": "Interview Scheduling Process",
        "content": (
            "Once an application clears preliminary screening, the talent acquisition coordinator initiates interview scheduling "
            "within two business days through the automated scheduling portal. Candidates are provided three distinct calendar slots "
            "to accommodate their current professional commitments. All technical and managerial rounds are conducted via verified video conferencing links "
            "with calendar invites dispatched at least twenty-four hours in advance. Rescheduling requests must be lodged at least twelve hours before the designated slot."
        ),
        "metadata": {
            "category": "interviews",
            "department": "Recruitment Operations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-03",
        "topic": "offer-negotiation policy",
        "title": "Offer Negotiation Policy",
        "content": (
            "Compensation offers are structured according to standardized market benchmarks and internal pay parity bands established for each grade. "
            "Candidates may request a compensation review by providing documented competing offers or proof of recent structural appraisal within three business days of receiving the letter. "
            "Revised terms require formal authorization from the departmental hiring manager and the Human Resources compensation committee. "
            "Once finalized, the official offer letter remains valid for five business days, after which unaccepted proposals automatically lapse."
        ),
        "metadata": {
            "category": "compensation",
            "department": "Total Rewards",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-04",
        "topic": "background-verification process",
        "title": "Background Verification Process",
        "content": (
            "All conditional offers are contingent upon the successful completion of a comprehensive background verification conducted by an empaneled third-party agency. "
            "The verification encompasses past employment tenure, educational degree authenticity, criminal history records, and identity checks via government portals. "
            "Candidates must submit scanned copies of relieving letters, salary slips for the previous three months, and highest qualification certificates within forty-eight hours of offer acceptance. "
            "Any material discrepancy or deliberate omission identified during the verification cycle constitutes grounds for immediate rescission of the employment offer."
        ),
        "metadata": {
            "category": "compliance",
            "department": "HR Compliance",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-05",
        "topic": "notice-period policy",
        "title": "Notice Period Policy",
        "content": (
            "Confirmed employees are subject to a mandatory notice period of sixty days upon tendering formal resignation through the HRMS portal. "
            "During the probationary period, the applicable notice duration is reduced to thirty calendar days for both the employer and employee. "
            "Early release or notice period buyout is strictly at the operational discretion of the reporting manager and department head, subject to formal approval. "
            "Departing staff must complete all knowledge transfer milestones and return assigned corporate assets before receiving final exit clearance."
        ),
        "metadata": {
            "category": "employment_terms",
            "department": "Employee Relations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-06",
        "topic": "referral-bonus policy",
        "title": "Employee Referral Bonus Policy",
        "content": (
            "Full-time employees who refer successful candidates for open positions are eligible for a referral bonus ranging from twenty-five thousand to seventy-five thousand INR, depending on the job grade. "
            "The referred applicant must apply directly via the internal referral tracking link prior to their initial resume screening. "
            "The referral bonus is disbursed in two equal installments: fifty percent upon the candidate completing sixty days of continuous service, and the balance upon completion of their probationary milestone. "
            "Members of the Human Resources talent acquisition team and direct hiring managers for the vacancy are excluded from referral bonus eligibility."
        ),
        "metadata": {
            "category": "benefits",
            "department": "Talent Acquisition",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-07",
        "topic": "internal-transfer eligibility",
        "title": "Internal Job Posting & Transfer Eligibility",
        "content": (
            "Employees who have completed at least twelve months of uninterrupted tenure in their current role and business unit are eligible to apply for internal job postings. "
            "Applicants must have secured a minimum performance rating of 'Meets Expectations' or above in their most recent annual review cycle. "
            "Employees with active disciplinary proceedings or formal performance improvement plans are strictly ineligible for internal lateral moves. "
            "Upon mutual selection, the releasing manager must facilitate a smooth handover and release the transferring team member within forty-five calendar days."
        ),
        "metadata": {
            "category": "career_mobility",
            "department": "People Operations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-08",
        "topic": "probation-period policy",
        "title": "Probation Period Policy",
        "content": (
            "All newly inducted full-time personnel undergo a standard probationary assessment period of six calendar months from their official joining date. "
            "A formal performance evaluation is conducted by the direct supervisor at the end of month five to review core key performance indicators. "
            "Based on operational feedback, management may either confirm employment, extend the probation by up to three additional months, or terminate service with statutory notice. "
            "Confirmed employment status takes effect only upon issuance of a formal written confirmation memorandum signed by the Head of HR."
        ),
        "metadata": {
            "category": "employment_terms",
            "department": "People Operations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-09",
        "topic": "remote-work eligibility",
        "title": "Remote and Hybrid Work Eligibility",
        "content": (
            "Roles designated as hybrid mandate physical attendance at designated regional offices for a minimum of two scheduled days per business week. "
            "Full remote working arrangements are restricted to approved specialized engineering and analytical roles after successful completion of the initial six-month probation period. "
            "Employees seeking temporary remote dispensation for compassionate or medical reasons must submit a formal request endorsed by their unit director and HR business partner. "
            "All remote staff must maintain secure high-speed internet connectivity and strictly operate from authorized corporate virtual private network endpoints."
        ),
        "metadata": {
            "category": "workplace",
            "department": "People Operations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-10",
        "topic": "diversity-hiring guidelines",
        "title": "Diversity and Equal Opportunity Hiring Guidelines",
        "content": (
            "Naukri recruitment operations mandate equal employment opportunities regardless of gender, sexual orientation, caste, religion, disability, or age. "
            "Hiring teams must maintain balanced candidate slates, ensuring at least one-third representation from underrepresented demographics in final interview panels. "
            "Structured rubric-based evaluations must be submitted for every evaluated candidate to eliminate unconscious bias in selection decisions. "
            "Periodic diversity audits are conducted by the corporate governance committee to monitor equity across all recruitment stages and salary proposals."
        ),
        "metadata": {
            "category": "governance",
            "department": "Diversity & Inclusion",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-11",
        "topic": "exit-interview process",
        "title": "Exit Interview and Offboarding Process",
        "content": (
            "The Human Resources department schedules a confidential exit interview with every departing employee during their final week of employment. "
            "The session gathers structured feedback regarding leadership quality, workplace culture, compensation equity, and reasons for transition. "
            "All feedback is anonymized and aggregated into quarterly retention analysis reports presented to executive leadership. "
            "Full and final financial settlement, along with the experience certificate and provident fund transfer documentation, is processed within thirty days of clearance."
        ),
        "metadata": {
            "category": "offboarding",
            "department": "Employee Relations",
            "version": "2026.1",
        },
    },
    {
        "doc_id": "KB-12",
        "topic": "applicant-data-retention policy",
        "title": "Applicant Data Retention and Privacy Policy",
        "content": (
            "Candidate application dossiers, resume records, and evaluation rubrics are retained in the recruitment database for a statutory maximum of twenty-four months. "
            "Applicants maintain the legal right to request complete data erasure or portfolio updates by submitting a written request to the Data Privacy Officer. "
            "Sensitive identifiers such as identity documents and unformatted contact numbers are encrypted at rest using industry-standard cryptographic algorithms. "
            "Expired application records that exceed the retention ceiling without active consent or ongoing litigation are permanently purged during scheduled biannual system sweeps."
        ),
        "metadata": {
            "category": "privacy",
            "department": "Legal & Compliance",
            "version": "2026.1",
        },
    },
]

DOCS_BY_TOPIC: Dict[str, Dict[str, Any]] = {
    doc["topic"]: doc for doc in KNOWLEDGE_BASE_DOCS
}
DOCS_BY_ID: Dict[str, Dict[str, Any]] = {
    doc["doc_id"]: doc for doc in KNOWLEDGE_BASE_DOCS
}
KNOWLEDGE_BASE_DOCS_BY_ID = DOCS_BY_ID
