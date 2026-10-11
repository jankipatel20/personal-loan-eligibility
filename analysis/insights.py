"""
analysis/insights.py
Quantitative analytics and sector comparisons derived from test_profiles.csv.
Produces:
1. Hard Gate Rejection Pareto (which rules trigger the most declines)
2. Sector Underwriting Comparison (PSU vs Private Bank vs NBFC vs Fintech)
3. Pricing & Risk Spread Matrix across Bureau bands
"""

import os
import csv
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_CSV = os.path.join(BASE_DIR, "outputs", "test_profiles.csv")
LENDER_DATA_CSV = os.path.join(BASE_DIR, "data", "lender_data.csv")

def run_insights():
    if not os.path.exists(TEST_CSV):
        raise FileNotFoundError(f"Missing {TEST_CSV}. Run tests/run_tests.py first.")

    with open(TEST_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Load lender categories
    lender_categories = {}
    if os.path.exists(LENDER_DATA_CSV):
        with open(LENDER_DATA_CSV, "r", encoding="utf-8") as f:
            l_reader = csv.DictReader(f)
            for lr in l_reader:
                lender_categories[lr["lender_name"]] = lr["category"]

    print("=" * 80)
    print("INSIGHT 1: HARD GATE REJECTION PARETO ANALYSIS")
    print("=" * 80)

    rejection_reasons = []
    for r in rows:
        if r["is_eligible"] == "NO":
            reasons = r["rejection_reasons"].split("; ")
            for reason in reasons:
                if "CIBIL" in reason:
                    rejection_reasons.append("Credit Score / Bureau Cutoff")
                elif "income" in reason.lower() or "salary" in reason.lower():
                    if "exhaust" in reason.lower() or "foir" in reason.lower():
                        rejection_reasons.append("FOIR / Excessive Debt Obligations")
                    elif "account" in reason.lower():
                        rejection_reasons.append("Mandatory Salary Account with Lender")
                    else:
                        rejection_reasons.append("Minimum Salary Gate Breach")
                elif "tenure" in reason.lower() or "experience" in reason.lower():
                    rejection_reasons.append("Employment Vintage / Stability")
                elif "age" in reason.lower():
                    rejection_reasons.append("Age Bounds / Superannuation Cap")
                elif "citizenship" in reason.lower():
                    rejection_reasons.append("Citizenship / Non-Resident Gate")
                else:
                    rejection_reasons.append("Capacity / Minimum Loan Size")

    reason_counts = Counter(rejection_reasons)
    total_rejections = sum(reason_counts.values())

    print(f"Total Rejection Triggers Recorded: {total_rejections}\n")
    print(f"{'Rejection Trigger Category':<40} | {'Count':<8} | {'Share of Declines':<15}")
    print("-" * 70)
    for cat, count in reason_counts.most_common():
        pct = (count / total_rejections) * 100
        print(f"{cat:<40} | {count:<8} | {pct:>14.1f}%")

    print("\n" + "=" * 80)
    print("INSIGHT 2: SECTOR UNDERWRITING COMPARISON (PSU vs Private vs NBFC vs Fintech)")
    print("=" * 80)

    sector_stats = defaultdict(lambda: {
        "evals": 0, "approvals": 0, "rates": [], "amounts": [], "best_matches": 0
    })

    for r in rows:
        lender = r["lender"]
        # Map lender category
        category = "Unknown"
        for l_key, cat in lender_categories.items():
            if l_key.lower() in lender.lower() or lender.lower() in l_key.lower():
                category = cat
                break
        if category == "Unknown":
            if any(p in lender.lower() for p in ["sbi", "baroda", "pnb", "canara", "union", "india"]):
                category = "PSU Bank"
            elif any(p in lender.lower() for p in ["hdfc", "icici", "axis", "kotak", "indusind", "idfc", "yes", "federal"]):
                category = "Private Bank"
            elif any(p in lender.lower() for p in ["bajaj", "tata", "dmi"]):
                category = "NBFC"
            else:
                category = "Fintech"

        sector = sector_stats[category]
        sector["evals"] += 1
        if r["is_eligible"] == "YES":
            sector["approvals"] += 1
            if r["offered_rate_pct"] != "N/A":
                sector["rates"].append(float(r["offered_rate_pct"]))
            if r["max_eligible_amount"] != "N/A":
                sector["amounts"].append(float(r["max_eligible_amount"]))
        if r["is_best_match"] == "YES":
            sector["best_matches"] += 1

    print(f"{'Sector':<18} | {'Approval Rate':<14} | {'Mean Rate':<12} | {'Mean Eligible Loan':<20} | {'Best Matches':<12}")
    print("-" * 85)
    for cat, data in sorted(sector_stats.items()):
        app_rate = (data["approvals"] / data["evals"] * 100) if data["evals"] > 0 else 0
        mean_rate = (sum(data["rates"]) / len(data["rates"])) if data["rates"] else 0
        mean_loan = (sum(data["amounts"]) / len(data["amounts"])) if data["amounts"] else 0
        print(f"{cat:<18} | {app_rate:>12.1f}% | {mean_rate:>10.2f}% | Rs. {mean_loan:>16,.0f} | {data['best_matches']:>10}")

    print("\n" + "=" * 80)
    print("INSIGHT 3: CIBIL SCORE vs RISK SPREAD SENSITIVITY")
    print("=" * 80)
    cibil_rates = defaultdict(list)
    for r in rows:
        if r["is_eligible"] == "YES" and r["offered_rate_pct"] != "N/A":
            score = int(r["cibil_score"])
            cibil_rates[score].append(float(r["offered_rate_pct"]))

    print(f"{'CIBIL Score':<12} | {'Eligible Lenders':<18} | {'Lowest Rate':<12} | {'Median Rate':<12} | {'Highest Rate':<12}")
    print("-" * 75)
    for score in sorted(cibil_rates.keys()):
        rates = sorted(cibil_rates[score])
        min_r = rates[0]
        med_r = rates[len(rates)//2]
        max_r = rates[-1]
        print(f"{score:<12} | {len(rates):>16} | {min_r:>10.2f}% | {med_r:>10.2f}% | {max_r:>10.2f}%")
    print("=" * 80)

if __name__ == "__main__":
    run_insights()
