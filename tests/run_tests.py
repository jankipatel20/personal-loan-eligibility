"""
tests/run_tests.py
Execution script for Personal Loan Eligibility Engine test suite.
Evaluates all profiles in tests/profiles.json against data/lender_rules.csv
and outputs full decision matrix to outputs/test_profiles.csv.
"""

import os
import sys
import json
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from model.schema import ApplicantProfile
from model.engine import PersonalLoanEngine

def run_all_tests():
    profiles_path = os.path.join(BASE_DIR, "tests", "profiles.json")
    outputs_csv = os.path.join(BASE_DIR, "outputs", "test_profiles.csv")
    os.makedirs(os.path.dirname(outputs_csv), exist_ok=True)

    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles_list = json.load(f)

    engine = PersonalLoanEngine()
    print("=" * 80)
    print(f"RUNNING TEST SUITE: {len(profiles_list)} PROFILES ACROSS 20 LENDERS")
    print("=" * 80)

    csv_rows = []
    headers = [
        "applicant_id", "applicant_name", "age", "monthly_income", "cibil_score",
        "existing_emis", "test_scenario", "lender", "is_eligible", "rejection_reasons",
        "offered_rate_pct", "max_eligible_amount", "requested_amount", "tenure_months",
        "monthly_emi", "is_best_match", "recommendation_rank"
    ]

    for p_data in profiles_list:
        profile = ApplicantProfile(
            applicant_id=p_data["applicant_id"],
            name=p_data["name"],
            age=p_data["age"],
            citizenship=p_data.get("citizenship", "Indian national"),
            city=p_data.get("city", "Mumbai"),
            city_tier=p_data.get("city_tier", "metro"),
            employment_type=p_data.get("employment_type", "salaried"),
            employer_category=p_data.get("employer_category", "listed_mnc"),
            work_experience_total=p_data.get("work_experience_total", 36),
            months_in_current_job=p_data.get("months_in_current_job", 18),
            net_monthly_income=p_data["net_monthly_income"],
            existing_salary_bank=p_data.get("existing_salary_bank", "HDFC Bank"),
            cibil_score=p_data["cibil_score"],
            existing_emi_total=p_data.get("existing_emi_total", 0.0),
            requested_amount=p_data.get("requested_amount", 500000.0),
            requested_tenure=p_data.get("requested_tenure", 60)
        )

        res = engine.evaluate(profile)

        print(f"\n[{profile.applicant_id}] {profile.name} (Age: {profile.age}, Salary: Rs {profile.net_monthly_income:,.0f}, CIBIL: {profile.cibil_score})")
        print(f"  Scenario : {p_data.get('test_scenario', '')}")
        print(f"  Results  : {res.eligible_count} Eligible / {res.rejected_count} Ineligible")
        if res.best_match:
            print(f"  Best Match: {res.best_match.lender} @ {res.best_match.offered_rate}% p.a. (Max Loan: Rs {res.best_match.max_eligible_amount:,.0f}, EMI: Rs {res.best_match.monthly_emi:,.0f})")
        else:
            print("  Best Match: None (Ineligible across all lenders)")

        # Record CSV rows
        ranked_lender_names = [d.lender for d in res.ranked_lenders]
        for lender_name, decision in res.decisions.items():
            is_best = (res.best_match and res.best_match.lender == lender_name)
            rank = ranked_lender_names.index(lender_name) + 1 if decision.is_eligible else "N/A"
            csv_rows.append([
                profile.applicant_id,
                profile.name,
                profile.age,
                profile.net_monthly_income,
                profile.cibil_score,
                profile.existing_emi_total,
                p_data.get("test_scenario", ""),
                lender_name,
                "YES" if decision.is_eligible else "NO",
                "; ".join(decision.rejection_reasons) if decision.rejection_reasons else "None",
                decision.offered_rate if decision.is_eligible else "N/A",
                decision.max_eligible_amount if decision.is_eligible else "N/A",
                profile.requested_amount,
                decision.max_tenure_months if decision.is_eligible else "N/A",
                decision.monthly_emi if decision.is_eligible else "N/A",
                "YES" if is_best else "NO",
                rank
            ])

    with open(outputs_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_rows)

    print("\n" + "=" * 80)
    print(f"TEST RUN COMPLETE: Saved {len(csv_rows)} evaluation rows to {outputs_csv}")
    print("=" * 80)

if __name__ == "__main__":
    run_all_tests()
