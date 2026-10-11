"""
analysis/monte_carlo.py
Simulates a seeded representative population of 10,000 retail loan applicants in India
and executes the 4-stage decision engine across all 20 lenders (200,000 decision evaluations).
Computes population-level Rejection Pareto distribution and sector-level underwriting metrics.
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from collections import Counter

BASE_DIR = r"D:\personal-loan-eligibility"
sys.path.insert(0, BASE_DIR)

from model.schema import ApplicantProfile
from model.engine import PersonalLoanEngine

def run_monte_carlo_simulation(n_samples: int = 10000, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    engine = PersonalLoanEngine()

    print(f"Generating seeded synthetic population of {n_samples:,} Indian retail applicants...")

    banks = ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", 
             "Punjab National Bank", "Bank of Baroda", "Union Bank of India", "Canara Bank", "Other"]
    bank_weights = [0.28, 0.22, 0.15, 0.10, 0.08, 0.05, 0.04, 0.03, 0.03, 0.02]

    cities = [("Mumbai", "metro"), ("Delhi", "metro"), ("Bengaluru", "metro"), 
              ("Pune", "metro"), ("Hyderabad", "metro"), ("Jaipur", "tier2"), 
              ("Indore", "tier2"), ("Nagpur", "tier2"), ("Patna", "tier3"), ("Ranchi", "tier3")]

    emp_categories = ["listed_mnc", "large_private", "govt_psu", "defence", "small_unlisted"]
    emp_weights = [0.25, 0.35, 0.15, 0.05, 0.20]

    rejection_counter = Counter()
    total_evaluations = 0
    total_rejections = 0
    eligible_evaluations = 0

    for i in range(n_samples):
        # 1. Demographics
        age = int(np.clip(np.random.normal(32, 8), 19, 64))
        citizenship = "Indian national" if random.random() < 0.985 else "Non-Resident / Expat"
        city, city_tier = random.choice(cities)
        
        # 2. Employment
        is_self_emp = random.random() < 0.15
        emp_type = "self_employed" if is_self_emp else "salaried"
        emp_cat = "not_applicable" if is_self_emp else np.random.choice(emp_categories, p=emp_weights)
        
        max_possible_exp = max(6, (age - 21) * 12)
        total_exp = int(np.clip(np.random.exponential(scale=48) + 6, 3, max_possible_exp))
        current_job_exp = int(np.clip(random.randint(2, min(total_exp, 72)), 1, total_exp))
        biz_vintage = total_exp if is_self_emp else None

        # 3. Income & Banking
        # Log-normal monthly income distribution around Rs 38,000
        net_income = float(np.round(np.clip(np.random.lognormal(mean=10.5, sigma=0.55), 8000, 300000), -2))
        salary_bank = np.random.choice(banks, p=bank_weights)

        # 4. Bureau & Debt
        # Truncated bimodal CIBIL distribution
        if random.random() < 0.75:
            cibil = int(np.clip(np.random.normal(745, 45), 640, 850))
        else:
            cibil = int(np.clip(np.random.normal(630, 40), 520, 680))

        # Existing EMIs
        has_debt = random.random() < 0.65
        if has_debt:
            foir_current = np.clip(np.random.beta(2, 5), 0.05, 0.75)
            existing_emi = float(np.round(net_income * foir_current, -2))
        else:
            existing_emi = 0.0

        # Requested loan
        req_amt = float(np.round(np.clip(net_income * random.uniform(4, 15), 50000, 2500000), -3))
        req_tenure = random.choice([24, 36, 48, 60])

        profile = ApplicantProfile(
            applicant_id=f"MC_{i+1:05d}",
            name=f"Applicant {i+1}",
            age=age,
            citizenship=citizenship,
            city=city,
            city_tier=city_tier,
            employment_type=emp_type,
            employer_category=emp_cat,
            work_experience_total=total_exp,
            months_in_current_job=current_job_exp,
            business_vintage=biz_vintage,
            net_monthly_income=net_income,
            existing_salary_bank=salary_bank,
            cibil_score=cibil,
            existing_emi_total=existing_emi,
            requested_amount=req_amt,
            requested_tenure=req_tenure
        )

        res = engine.evaluate(profile)

        for lender, dec in res.decisions.items():
            total_evaluations += 1
            if dec.is_eligible:
                eligible_evaluations += 1
            else:
                total_rejections += 1
                # Categorize rejection reasons
                for r in dec.rejection_reasons:
                    r_lower = r.lower()
                    if "cibil" in r_lower or "cutoff" in r_lower:
                        rejection_counter["Credit Bureau / CIBIL Cutoff"] += 1
                    elif "employment type" in r_lower or "requires salaried" in r_lower:
                        rejection_counter["Employment Type Ineligible (Salaried Mandate)"] += 1
                    elif "monthly income" in r_lower or "below minimum requirement" in r_lower:
                        rejection_counter["Minimum Income Floor Gate"] += 1
                    elif "foir" in r_lower or "exhaust" in r_lower:
                        rejection_counter["Debt Capacity / FOIR Ceiling Exhausted"] += 1
                    elif "salary account with" in r_lower:
                        rejection_counter["Mandatory Salary Account with Lender"] += 1
                    elif "current job tenure" in r_lower or "work experience" in r_lower or "vintage" in r_lower:
                        rejection_counter["Job Stability / Experience Vintage Gate"] += 1
                    elif "age" in r_lower or "maturity" in r_lower or "superannuation" in r_lower:
                        rejection_counter["Age Bounds / Superannuation Cap"] += 1
                    elif "citizenship" in r_lower:
                        rejection_counter["Citizenship / Non-Resident Gate"] += 1
                    elif "minimum loan ticket" in r_lower or "borrowing capacity" in r_lower:
                        rejection_counter["Ticket Size / Minimum Quantum Floor"] += 1
                    else:
                        rejection_counter["Other Policy Criteria"] += 1

    print("\n" + "=" * 80)
    print("POPULATION-LEVEL REJECTION PARETO ANALYSIS (10,000 APPLICANTS, 200,000 EVALUATIONS)")
    print("=" * 80)
    print(f"Total Decision Evaluations : {total_evaluations:,}")
    print(f"Eligible Evaluations       : {eligible_evaluations:,} ({eligible_evaluations/total_evaluations*100:.1f}%)")
    print(f"Ineligible Evaluations     : {total_rejections:,} ({total_rejections/total_evaluations*100:.1f}%)")
    print(f"Total Rejection Triggers   : {sum(rejection_counter.values()):,}\n")

    total_triggers = sum(rejection_counter.values())
    sorted_triggers = rejection_counter.most_common()

    print(f"{'Rejection Trigger Category':<45} | {'Count':<8} | {'Share (%)':<10} | {'Cumulative (%)'}")
    print("-" * 80)
    cum = 0.0
    results_list = []
    for cat, cnt in sorted_triggers:
        share = (cnt / total_triggers) * 100.0
        cum += share
        print(f"{cat:<45} | {cnt:<8,d} | {share:>8.1f}% | {cum:>12.1f}%")
        results_list.append({"category": cat, "count": cnt, "share": share, "cumulative": cum})

    return results_list

if __name__ == "__main__":
    run_monte_carlo_simulation(10000, seed=42)
