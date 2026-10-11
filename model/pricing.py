"""
model/pricing.py
Deterministic scorecard and risk-based pricing engine.
Maps applicant CIBIL bracket, employer category, and relationship to lender rate bands.
"""

def calculate_offered_rate(
    base_rate: float,
    max_rate: float,
    cibil_score: int,
    employer_category: str = "listed_mnc",
    is_existing_customer: bool = False
) -> float:
    """
    Computes deterministic offered interest rate within [base_rate, max_rate] band.
    - Bureau tiers: 750+ (prime), 700-749 (tier 2), 650-699 (tier 3), <650 (high risk).
    - Employer adjustments: Govt/Defence (-0.25%), Super-A listed (-0.10%), unlisted (+0.50%).
    - Relationship adjustment: Existing customer (-0.20%).
    """
    # 1. Bureau Base Placement
    if cibil_score >= 780:
        band_fraction = 0.00  # Lowest rate
    elif cibil_score >= 750:
        band_fraction = 0.08
    elif cibil_score >= 720:
        band_fraction = 0.25
    elif cibil_score >= 700:
        band_fraction = 0.45
    elif cibil_score >= 650:
        band_fraction = 0.70
    else:
        band_fraction = 0.95

    rate = base_rate + (max_rate - base_rate) * band_fraction

    # 2. Employer Category Risk Spread
    emp_adj = {
        "defence": -0.30,
        "govt_psu": -0.25,
        "listed_mnc": 0.00,
        "large_private": 0.20,
        "small_unlisted": 0.60,
        "not_applicable": 1.00
    }.get(employer_category.lower(), 0.20)

    # 3. Relationship discount
    rel_adj = -0.25 if is_existing_customer else 0.00

    final_rate = rate + emp_adj + rel_adj
    return round(max(base_rate, min(max_rate, final_rate)), 2)


def calculate_monthly_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Standard reducing-balance monthly amortization formula."""
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    if r == 0:
        return round(principal / tenure_months, 2)
    factor = (1.0 + r) ** tenure_months
    emi = principal * r * factor / (factor - 1.0)
    return round(emi, 2)


def calculate_loan_from_emi(max_emi: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Inverts reducing balance amortization formula to compute max loan from permissible EMI."""
    if max_emi <= 0 or tenure_months <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    if r == 0:
        return round(max_emi * tenure_months, 2)
    factor = (1.0 + r) ** tenure_months
    loan = max_emi * (factor - 1.0) / (r * factor)
    return round(loan, 2)
