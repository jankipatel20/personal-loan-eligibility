"""
tests/run_tests.py
Execution script for Personal Loan Eligibility Engine test suite.
Evaluates all profiles in tests/profiles.json against data/lender_rules.csv,
outputs full decision matrix to outputs/test_profiles.csv with ranking rationale,
and automatically synchronizes the Section 8 results table in README.md.
"""

import os
import sys
import json
import csv
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from model.schema import ApplicantProfile
from model.engine import PersonalLoanEngine


def run_all_tests():
    profiles_path = os.path.join(BASE_DIR, "tests", "profiles.json")
    outputs_csv = os.path.join(BASE_DIR, "outputs", "test_profiles.csv")
    readme_path = os.path.join(BASE_DIR, "README.md")
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
        "monthly_emi", "is_best_match", "recommendation_rank", "best_match_rationale"
    ]

    summary_table_rows = []

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
            business_vintage=p_data.get("business_vintage"),
            annual_income_itr=p_data.get("annual_income_itr"),
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
            print(f"  Best Match: {res.best_match.lender} @ {res.best_match.offered_rate:.2f}% p.a. (Max Loan: Rs {res.best_match.max_eligible_amount:,.0f}, EMI: Rs {res.best_match.monthly_emi:,.0f})")
        else:
            print("  Best Match: None (Ineligible across all lenders)")

        # Prepare summary row for README
        if res.best_match:
            b_lender = res.best_match.lender
            b_rate = f"{res.best_match.offered_rate:.2f}%"
            b_amt = f"Rs {int(res.best_match.max_eligible_amount):,}"
        else:
            b_lender = "*None (All Filtered)*"
            b_rate = "N/A"
            b_amt = "Rs 0"

        scen_summary = p_data.get("test_scenario", "").split(":")[0] if ":" in p_data.get("test_scenario", "") else p_data.get("test_scenario", "")
        summary_table_rows.append(
            f"| `{profile.applicant_id[:4]}` | {profile.name} | {scen_summary} | "
            f"Rs {int(profile.net_monthly_income):,} | {profile.cibil_score} | "
            f"Rs {int(profile.existing_emi_total):,} | {res.eligible_count} / 20 | "
            f"{b_lender} | {b_rate} | {b_amt} |"
        )

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
                f"{decision.offered_rate:.2f}" if decision.is_eligible and decision.offered_rate is not None else "N/A",
                decision.max_eligible_amount if decision.is_eligible else "N/A",
                profile.requested_amount,
                decision.max_tenure_months if decision.is_eligible else "N/A",
                decision.monthly_emi if decision.is_eligible else "N/A",
                "YES" if is_best else "NO",
                rank,
                res.recommendation_rationale if is_best else (decision.explanation if decision.is_eligible else "; ".join(decision.rejection_reasons))
            ])

    with open(outputs_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_rows)

    print("\n" + "=" * 80)
    print(f"TEST RUN COMPLETE: Saved {len(csv_rows)} evaluation rows to {outputs_csv}")
    print("=" * 80)

    # Automatically synchronize Section 8 table in README.md
    if os.path.exists(readme_path):
        sync_readme_section_8(readme_path, summary_table_rows)


def sync_readme_section_8(readme_path: str, summary_rows: list):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    table_header = (
        "| Profile ID | Candidate | Scenario Tested | Net Income | CIBIL | Existing EMI | Eligible Lenders | Best Match Lender | Best Offered APR | Max Approved Quantum |\n"
        "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |"
    )
    table_body = "\n".join(summary_rows)
    new_table = f"{table_header}\n{table_body}"

    # Regex to find the table inside section 8
    pattern = r"(\| Profile ID \| Candidate \|.*?\n\| :--- \|.*?\n(?:\| `P_\d+` \|.*?\n)+)"
    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_table + "\n", content)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("Successfully synchronized Section 8 table in README.md (Zero-Drift Guarantee)")
    else:
        print("Note: Section 8 table pattern not matched for in-place replacement.")


if __name__ == "__main__":
    run_all_tests()
