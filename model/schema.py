"""
model/schema.py
Data structures and schema definitions for Personal Loan Eligibility Engine.
Conforms to data/variables.csv (19 input variables) and lender rules schema.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ApplicantProfile:
    # 1. Identity & Demographics
    applicant_id: str
    name: str
    age: int
    citizenship: str = "Indian national"
    city: str = "Mumbai"
    city_tier: str = "metro"  # metro, tier1, tier2, tier3

    # 2. Employment & Vintage
    employment_type: str = "salaried"  # salaried, self_employed_professional, self_employed_business, pensioner
    employer_category: str = "listed_mnc"  # govt_psu, defence, listed_mnc, large_private, small_unlisted
    work_experience_total: int = 36  # in months
    months_in_current_job: int = 18  # in months
    business_vintage: Optional[int] = None

    # 3. Income & Banking
    net_monthly_income: float = 50000.0  # Take-home monthly pay in INR
    gross_monthly_income: Optional[float] = None
    annual_income_itr: Optional[float] = None
    existing_salary_bank: str = "HDFC Bank"

    # 4. Bureau & Debt
    cibil_score: int = 760  # -1 for no history, else 300-900
    existing_emi_total: float = 0.0  # Sum of active monthly EMIs
    recent_enquiries_6m: int = 0
    past_delays_flag: bool = False

    # 5. Loan Request
    requested_amount: float = 500000.0
    requested_tenure: int = 60  # in months

    def __post_init__(self):
        if self.gross_monthly_income is None:
            # Conservative gross estimate if not provided (assume 18% deductions)
            self.gross_monthly_income = round(self.net_monthly_income / 0.82, 2)


@dataclass
class LenderDecision:
    lender: str
    product_name: str
    is_eligible: bool
    rejection_reasons: List[str] = field(default_factory=list)
    
    # Financial terms if eligible
    offered_rate: Optional[float] = None  # in % p.a.
    max_eligible_amount: Optional[float] = None  # in INR
    max_tenure_months: Optional[int] = None  # in months
    monthly_emi: Optional[float] = None  # in INR
    processing_fee_estimate: Optional[str] = None
    foreclosure_terms: Optional[str] = None
    
    # Internal capacity metrics
    foir_cap_used: Optional[float] = None  # in %
    multiplier_cap_used: Optional[float] = None  # multiple of salary
    max_emi_capacity: Optional[float] = None  # max permissible EMI room
    explanation: str = ""


@dataclass
class EngineResult:
    applicant_id: str
    applicant_name: str
    total_lenders_evaluated: int
    eligible_count: int
    rejected_count: int
    decisions: Dict[str, LenderDecision]
    ranked_lenders: List[LenderDecision]
    best_match: Optional[LenderDecision] = None
    recommendation_rationale: str = ""
