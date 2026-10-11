"""
model/engine.py
Core 4-Stage Personal Loan Eligibility & Recommendation Engine.
Evaluates an ApplicantProfile against the 20 lenders loaded from data/lender_rules.csv.
"""

import os
import csv
from typing import Dict, List, Optional, Any
from model.schema import ApplicantProfile, LenderDecision, EngineResult
from model.pricing import calculate_offered_rate, calculate_monthly_emi, calculate_loan_from_emi

class PersonalLoanEngine:
    def __init__(self, rules_csv_path: Optional[str] = None):
        if rules_csv_path is None:
            rules_csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "lender_rules.csv"
            )
        self.rules_csv_path = rules_csv_path
        self.rules_by_lender = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Loads and indexes rules by lender from data/lender_rules.csv."""
        lenders_data: Dict[str, Dict[str, Any]] = {}
        if not os.path.exists(self.rules_csv_path):
            raise FileNotFoundError(f"Lender rules dataset not found at {self.rules_csv_path}")

        with open(self.rules_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lender = row["lender"]
                if lender not in lenders_data:
                    lenders_data[lender] = {
                        "lender": lender,
                        "product_name": row["product_name"],
                        "rules": {}
                    }
                r_name = row["rule_name"]
                lenders_data[lender]["rules"][r_name] = {
                    "rule_id": row["rule_id"],
                    "operator": row["operator"],
                    "value": row["rule_value"],
                    "unit": row["unit"],
                    "is_estimate": row["is_estimate"],
                    "raw_quote": row.get("raw_quote", "")
                }
        return lenders_data

    def evaluate(self, profile: ApplicantProfile) -> EngineResult:
        """Evaluates an applicant profile against all 20 lenders across 4 stages."""
        decisions: Dict[str, LenderDecision] = {}

        for lender_name, lender_info in self.rules_by_lender.items():
            decision = self._evaluate_lender(profile, lender_name, lender_info)
            decisions[lender_name] = decision

        # Stage 4: Ranking & Best Match
        eligible_lenders = [d for d in decisions.values() if d.is_eligible]
        
        # Sort key: 1. Lowest Offered Rate, 2. Highest Eligible Amount
        ranked = sorted(
            eligible_lenders,
            key=lambda x: (x.offered_rate or 999.0, -(x.max_eligible_amount or 0.0))
        )

        best_match = ranked[0] if ranked else None
        rationale = ""
        if best_match:
            rationale = (
                f"Ranked #1 Best Match: {best_match.lender} offers the lowest interest rate "
                f"({best_match.offered_rate}% p.a.) with a loan quantum of Rs. {best_match.max_eligible_amount:,.2f} "
                f"and monthly EMI of Rs. {best_match.monthly_emi:,.2f}."
            )
        else:
            rationale = "Applicant is currently ineligible across all evaluated lenders due to hard gate/capacity limits."

        return EngineResult(
            applicant_id=profile.applicant_id,
            applicant_name=profile.name,
            total_lenders_evaluated=len(self.rules_by_lender),
            eligible_count=len(eligible_lenders),
            rejected_count=len(decisions) - len(eligible_lenders),
            decisions=decisions,
            ranked_lenders=ranked,
            best_match=best_match,
            recommendation_rationale=rationale
        )

    def _evaluate_lender(self, p: ApplicantProfile, lender: str, info: Dict[str, Any]) -> LenderDecision:
        rules = info["rules"]
        product_name = info["product_name"]
        rejection_reasons: List[str] = []

        # ============================================================
        # STAGE 1: HARD GATES EVALUATION
        # ============================================================
        
        # 1. Citizenship / Nationality
        if "nationality" in rules:
            req_nat = rules["nationality"]["value"]
            if p.citizenship.lower() != req_nat.lower():
                rejection_reasons.append(f"Citizenship '{p.citizenship}' does not meet required '{req_nat}'")

        # 2. Minimum Age
        min_age = 21
        for k in ["min_age", "applicant_identity_min_age"]:
            if k in rules:
                min_age = float(rules[k]["value"])
                break
        if p.age < min_age:
            rejection_reasons.append(f"Age {p.age} is below minimum requirement of {int(min_age)} years")

        # 3. Maximum Age at Application
        max_app_age = 60
        for k in ["max_age_application", "applicant_identity_max_age_application"]:
            if k in rules:
                max_app_age = float(rules[k]["value"])
                break
        if p.age > max_app_age:
            rejection_reasons.append(f"Age {p.age} exceeds maximum application age of {int(max_app_age)} years")

        # 4. Maximum Age at Loan Maturity
        max_mat_age = 60
        for k in ["max_age_maturity", "applicant_identity_max_age_maturity"]:
            if k in rules:
                max_mat_age = float(rules[k]["value"])
                break
        tenure_requested_years = p.requested_tenure / 12.0
        if (p.age + tenure_requested_years) > max_mat_age:
            # Check if applicant can be given a shorter tenure
            remaining_tenure_months = int((max_mat_age - p.age) * 12)
            if remaining_tenure_months < 12:
                rejection_reasons.append(
                    f"Age at maturity ({p.age + tenure_requested_years:.1f}y) exceeds {int(max_mat_age)}y superannuation cap"
                )

        # 5. Work Experience / Stability
        min_total_exp = 12
        for k in ["min_total_experience", "employment_stability_min_total_experience"]:
            if k in rules:
                min_total_exp = float(rules[k]["value"])
                break
        if p.work_experience_total < min_total_exp:
            rejection_reasons.append(
                f"Total work experience {p.work_experience_total}m is below required {int(min_total_exp)}m"
            )

        min_current_job = 6
        for k in ["min_current_job_tenure", "employment_stability_min_current_job_tenure"]:
            if k in rules:
                min_current_job = float(rules[k]["value"])
                break
        if p.months_in_current_job < min_current_job:
            rejection_reasons.append(
                f"Current job tenure {p.months_in_current_job}m is below required {int(min_current_job)}m"
            )

        # 6. Minimum Monthly Salary Gate
        min_salary = 15000.0
        for k in ["min_monthly_net_income", "min_monthly_income", "income_min_monthly_income"]:
            if k in rules:
                try:
                    min_salary = float(rules[k]["value"])
                except ValueError:
                    pass
                break
        if p.net_monthly_income < min_salary:
            rejection_reasons.append(
                f"Net monthly income Rs. {p.net_monthly_income:,.2f} is below minimum requirement of Rs. {min_salary:,.2f}"
            )

        # 7. Credit Bureau / CIBIL Cutoff
        min_cibil = 650
        for k in ["min_cibil_score", "credit_bureau_min_cibil_score"]:
            if k in rules:
                try:
                    min_cibil = float(rules[k]["value"])
                except ValueError:
                    pass
                break
        if p.cibil_score < min_cibil:
            rejection_reasons.append(
                f"CIBIL score {p.cibil_score} is below minimum cutoff threshold of {int(min_cibil)}"
            )

        # 8. Mandatory Salary Account with Lender
        sal_acc_req = False
        for k in ["salary_account_required", "income_salary_account_required"]:
            if k in rules and rules[k]["value"].lower() == "true":
                sal_acc_req = True
                break
        if sal_acc_req:
            # Check if applicant banks with this lender
            lender_short = lender.split()[0].lower()
            if lender_short not in p.existing_salary_bank.lower():
                rejection_reasons.append(
                    f"Mandatory salary account with {lender} required (applicant banks with {p.existing_salary_bank})"
                )

        if rejection_reasons:
            return LenderDecision(
                lender=lender,
                product_name=product_name,
                is_eligible=False,
                rejection_reasons=rejection_reasons,
                explanation=f"Ineligible: {'; '.join(rejection_reasons)}"
            )

        # ============================================================
        # STAGE 2: CAPACITY & FOIR EVALUATION
        # ============================================================
        
        # 1. FOIR Limit
        foir_limit = 50.0  # default 50%
        for k in ["foir_limit", "repayment_capacity_foir_limit", "max_foir_limit"]:
            if k in rules:
                try:
                    foir_limit = float(rules[k]["value"])
                except ValueError:
                    pass
                break

        # Income base for FOIR
        max_permissible_emi_total = p.net_monthly_income * (foir_limit / 100.0)
        available_emi_room = max_permissible_emi_total - p.existing_emi_total

        if available_emi_room <= 0:
            return LenderDecision(
                lender=lender,
                product_name=product_name,
                is_eligible=False,
                rejection_reasons=[
                    f"Existing EMIs (Rs. {p.existing_emi_total:,.2f}) exhaust permissible {foir_limit}% FOIR capacity (Rs. {max_permissible_emi_total:,.2f})"
                ],
                foir_cap_used=foir_limit,
                explanation="Ineligible due to excessive existing debt obligations (FOIR breach)."
            )

        # 2. Tenure bounds
        min_tenure = 12
        max_tenure = 60
        for k in ["min_tenure_months", "tenure_min_tenure_months"]:
            if k in rules:
                try: min_tenure = int(float(rules[k]["value"]))
                except: pass
        for k in ["max_tenure_months", "tenure_max_tenure_months"]:
            if k in rules:
                try: max_tenure = int(float(rules[k]["value"]))
                except: pass

        # Clamp tenure to retirement age
        retirement_tenure_limit = max(12, int((max_mat_age - p.age) * 12))
        effective_tenure = min(p.requested_tenure, max_tenure, retirement_tenure_limit)
        effective_tenure = max(min_tenure, effective_tenure)

        # ============================================================
        # STAGE 3: PRICING & QUANTUM CLAMPING
        # ============================================================
        
        # 1. Rate Pricing
        starting_rate = 10.50
        max_rate = 22.00
        for k in ["starting_interest_rate", "pricing_starting_interest_rate"]:
            if k in rules:
                try: starting_rate = float(rules[k]["value"])
                except: pass
        for k in ["max_interest_rate", "pricing_max_interest_rate"]:
            if k in rules:
                try: max_rate = float(rules[k]["value"])
                except: pass

        is_existing_cust = lender.split()[0].lower() in p.existing_salary_bank.lower()
        offered_rate = calculate_offered_rate(
            base_rate=starting_rate,
            max_rate=max_rate,
            cibil_score=p.cibil_score,
            employer_category=p.employer_category,
            is_existing_customer=is_existing_cust
        )

        # 2. Quantum from EMI Capacity
        capacity_from_emi = calculate_loan_from_emi(
            max_emi=available_emi_room,
            annual_rate_pct=offered_rate,
            tenure_months=effective_tenure
        )

        # 3. Salary Multiplier Cap
        salary_multiplier = 20.0
        for k in ["salary_multiplier_cap", "salary_multiple_cap", "disposable_income_multiplier"]:
            if k in rules:
                try: salary_multiplier = float(rules[k]["value"])
                except: pass
                break
        multiplier_cap = p.net_monthly_income * salary_multiplier

        # 4. Lender Absolute Quantum Bounds
        min_loan_amt = 25000.0
        max_loan_amt = 4000000.0
        for k in ["min_loan_amount", "loan_amount_min_loan_amount"]:
            if k in rules:
                try: min_loan_amt = float(rules[k]["value"])
                except: pass
        for k in ["max_loan_amount", "loan_amount_max_loan_amount"]:
            if k in rules:
                try: max_loan_amt = float(rules[k]["value"])
                except: pass

        # Final Eligible Quantum
        eligible_quantum = min(capacity_from_emi, multiplier_cap, max_loan_amt)

        if eligible_quantum < min_loan_amt:
            return LenderDecision(
                lender=lender,
                product_name=product_name,
                is_eligible=False,
                rejection_reasons=[
                    f"Assessed borrowing capacity (Rs. {eligible_quantum:,.2f}) is below minimum loan ticket (Rs. {min_loan_amt:,.2f})"
                ],
                explanation="Ineligible: Repayment capacity below minimum loan size."
            )

        # Sanctioned loan is minimum of requested amount and max eligible quantum
        sanctioned_amount = min(p.requested_amount, eligible_quantum)
        final_emi = calculate_monthly_emi(sanctioned_amount, offered_rate, effective_tenure)

        # Charges
        proc_fee = rules.get("processing_fee", {}).get("value", "1.00% to 2.00% + GST")
        foreclosure = rules.get("foreclosure_charges", {}).get("value", "Nil on floating")

        return LenderDecision(
            lender=lender,
            product_name=product_name,
            is_eligible=True,
            offered_rate=offered_rate,
            max_eligible_amount=round(eligible_quantum, 2),
            max_tenure_months=effective_tenure,
            monthly_emi=final_emi,
            processing_fee_estimate=proc_fee,
            foreclosure_terms=foreclosure,
            foir_cap_used=foir_limit,
            multiplier_cap_used=salary_multiplier,
            max_emi_capacity=round(available_emi_room, 2),
            explanation=(
                f"Eligible for up to Rs. {eligible_quantum:,.2f} at {offered_rate}% p.a. for {effective_tenure}m. "
                f"Requested Rs. {sanctioned_amount:,.2f} approved with Monthly EMI of Rs. {final_emi:,.2f}."
            )
        )
