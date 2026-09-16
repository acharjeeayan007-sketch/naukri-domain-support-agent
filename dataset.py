"""
dataset.py - Seeded job application dataset generator for internal testing and development.

Simulates Naukri.com applicant records for talent pipeline staging:
- Categories: Software Engineer, Data Analyst, Product Manager, HR Executive, Sales Associate
- Compensation ranges calibrated to Indian tech/corporate salary bands (₹4.5L - ₹42L INR)
- Status lifecycle: Applied -> Screening -> Interview Scheduled -> Offered / Rejected
- Priority review flags for expedited hiring workflows
"""

from collections import Counter
import json
import random
from typing import Any, Dict, List, Optional

# Fixed seed for repeatable local staging runs
DATASET_SEED = 42

CATEGORIES = [
    "Software Engineer",
    "Data Analyst",
    "Product Manager",
    "HR Executive",
    "Sales Associate",
]

CATEGORY_WEIGHTS = [0.30, 0.20, 0.18, 0.16, 0.16]

STATUSES = [
    "Applied",
    "Screening",
    "Interview Scheduled",
    "Offered",
    "Rejected",
]

STATUS_WEIGHTS = [0.28, 0.26, 0.22, 0.12, 0.12]

# Realistic salary ranges (min_inr, max_inr) per category based on Naukri.com market tiers
SALARY_RANGES_BY_CATEGORY = {
    "Software Engineer": (600_000, 4_200_000),
    "Data Analyst": (500_000, 2_400_000),
    "Product Manager": (1_200_000, 3_800_000),
    "HR Executive": (450_000, 1_600_000),
    "Sales Associate": (450_000, 1_800_000),
}


def generate_job_applications(seed: int = DATASET_SEED, count: int = 50) -> List[Dict[str, Any]]:
    """
    Generates a deterministic list of job application records.
    """
    rng = random.Random(seed)
    applications: List[Dict[str, Any]] = []

    for idx in range(1, count + 1):
        record_id = f"APP-{1000 + idx}"
        category = rng.choices(CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
        status = rng.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        
        salary_min, salary_max = SALARY_RANGES_BY_CATEGORY[category]
        # Round salary to nearest 25,000 INR for realistic compensation proposals
        raw_salary = rng.randint(salary_min, salary_max)
        expected_salary_inr = int(round(raw_salary / 25000.0) * 25000)
        
        days_since_created = rng.randint(0, 30)
        flagged_priority_review = rng.random() < 0.20

        record = {
            "record_id": record_id,
            "category": category,
            "status": status,
            "expected_salary_inr": expected_salary_inr,
            "days_since_created": days_since_created,
            "flagged_priority_review": flagged_priority_review,
        }
        applications.append(record)

    return applications


# Instantiate the canonical dataset
JOB_APPLICATIONS: List[Dict[str, Any]] = generate_job_applications(DATASET_SEED, 50)
JOB_APPLICATIONS_BY_ID: Dict[str, Dict[str, Any]] = {
    rec["record_id"]: rec for rec in JOB_APPLICATIONS
}


def validate_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates the dataset against all Task 1 constraints.
    Returns metrics and assertion results.
    """
    total = len(records)
    assert total >= 40, f"Total records must be >= 40, found {total}"

    cat_counts = Counter(r["category"] for r in records)
    for cat in CATEGORIES:
        count = cat_counts.get(cat, 0)
        assert count >= 3, f"Category '{cat}' must have >= 3 records, found {count}"

    status_counts = Counter(r["status"] for r in records)
    for stat in STATUSES:
        count = status_counts.get(stat, 0)
        assert count >= 1, f"Status '{stat}' must have >= 1 record, found {count}"

    flagged_count = sum(1 for r in records if r["flagged_priority_review"])
    flagged_pct = (flagged_count / total) * 100.0
    assert 10.0 <= flagged_pct <= 30.0, (
        f"Flagged priority percentage must be in [10%, 30%], found {flagged_pct:.2f}%"
    )

    for r in records:
        assert 0 <= r["days_since_created"] <= 30, (
            f"days_since_created must be 0-30, found {r['days_since_created']}"
        )
        assert 450_000 <= r["expected_salary_inr"] <= 4_200_000, (
            f"Salary out of range: {r['expected_salary_inr']}"
        )

    return {
        "total_records": total,
        "category_counts": dict(cat_counts),
        "status_counts": dict(status_counts),
        "flagged_count": flagged_count,
        "flagged_percentage": round(flagged_pct, 2),
        "is_valid": True,
    }


def report_dataset_summary() -> str:
    """Generates formatted summary report string for transcripts and README."""
    metrics = validate_dataset(JOB_APPLICATIONS)
    lines = [
        "=================================================================",
        "NAUKRI.COM RECRUITMENT DOMAIN SUPPORT AGENT - DATASET VALIDATION",
        "=================================================================",
        f"Total Records Generated: {metrics['total_records']} (Constraint: >= 40)",
        f"Deterministic Generator Seed: {DATASET_SEED}",
        "",
        "Category Counts (Constraint: Every given category >= 3 records):",
    ]
    for cat in CATEGORIES:
        lines.append(f"  - {cat:20s}: {metrics['category_counts'].get(cat, 0):2d} records")

    lines.append("")
    lines.append("Status Coverage (Constraint: Every given status >= 1 record):")
    for stat in STATUSES:
        lines.append(f"  - {stat:20s}: {metrics['status_counts'].get(stat, 0):2d} records")

    lines.append("")
    lines.append(
        f"Flagged Priority Review: {metrics['flagged_count']}/{metrics['total_records']} "
        f"({metrics['flagged_percentage']:.1f}%) [Constraint: 10% - 30%]"
    )
    lines.append(
        "Expected Salary Range: INR 4,50,000 to INR 42,00,000 (Min: ₹4,50,000, Max: ₹42,00,000)"
    )
    lines.append(
        "Reasoning: The expected salary ranges from ₹4,50,000 to ₹42,00,000 INR based on current "
        "Indian recruitment benchmarks on Naukri.com, capturing entry-level to senior roles across "
        "technical, product, HR, and sales verticals."
    )
    lines.append("Validation Status: PASSED (All acceptance criteria satisfied)")
    lines.append("=================================================================")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report_dataset_summary())
    print("\nFirst 3 Sample Records:")
    print(json.dumps(JOB_APPLICATIONS[:3], indent=2))
