"""
Reverse-Engineering Helper Tool for Personal Loan Public Calculators
Usage:
  Interactive Mode:
    python research/reverse_engineer.py

  CLI Mode:
    python research/reverse_engineer.py --lender "HDFC Bank" --income 50000 --loan 1000000 --rate 11.0 --tenure 60 --existing_emi 0
"""

import sys
import argparse

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    monthly_rate = (annual_rate / 100.0) / 12.0
    if monthly_rate <= 0:
        return principal / tenure_months
    factor = (1.0 + monthly_rate) ** tenure_months
    return principal * (monthly_rate * factor) / (factor - 1.0)

def analyze(lender: str, income: float, loan: float, rate: float, tenure: int, existing_emi: float = 0.0):
    emi = calculate_emi(loan, rate, tenure)
    total_obligation = emi + existing_emi
    foir = (total_obligation / income) * 100.0 if income > 0 else 0.0
    multiple = (loan / income) if income > 0 else 0.0

    print("\n" + "=" * 65)
    print(f"  ANALYSIS REPORT: {lender.upper()}")
    print("=" * 65)
    print(f"  Monthly Take-Home Salary : Rs. {income:,.0f}")
    print(f"  Existing Monthly EMIs    : Rs. {existing_emi:,.0f}")
    print(f"  Eligible Loan Amount     : Rs. {loan:,.0f}")
    print(f"  Assumed Interest Rate    : {rate:.2f}% p.a.")
    print(f"  Tenure                   : {tenure} months ({tenure/12:.1f} years)")
    print("-" * 65)
    print(f"  [REVERSE-ENGINEERED UNDERWRITING METRICS]")
    print(f"  Implied Monthly EMI      : Rs. {emi:,.0f} / month")
    print(f"  Implied Total FOIR / DTI : {foir:.2f}%")
    print(f"  Implied Salary Multiple  : {multiple:.1f}x Net Monthly Salary")
    print("-" * 65)
    
    foir_rounded = round(foir)
    mult_rounded = round(multiple)
    
    print("  READY-TO-USE ROWS FOR 09_extracted_rules.csv:")
    print(f"  repayment_capacity,foir_limit,<=,{foir_rounded},percent,derived,medium,yes")
    print(f"  loan_amount,salary_multiple_cap,<=,{mult_rounded},multiple,derived,medium,yes")
    print("=" * 65 + "\n")
    
    return {
        "emi": emi,
        "foir": foir,
        "multiple": multiple
    }

def main():
    parser = argparse.ArgumentParser(description="Reverse engineer bank calculator outputs.")
    parser.add_argument("--lender", type=str, default="HDFC Bank", help="Lender name")
    parser.add_argument("--income", type=float, default=None, help="Net monthly salary in INR")
    parser.add_argument("--loan", type=float, default=None, help="Eligible loan amount in INR")
    parser.add_argument("--rate", type=float, default=11.0, help="Interest rate in percentage")
    parser.add_argument("--tenure", type=int, default=60, help="Tenure in months")
    parser.add_argument("--existing_emi", type=float, default=0.0, help="Existing monthly EMIs in INR")

    args = parser.parse_args()

    if args.income is not None and args.loan is not None:
        analyze(args.lender, args.income, args.loan, args.rate, args.tenure, args.existing_emi)
    else:
        print("\n=== Reverse Engineering Tool for Public Loan Calculators ===")
        lender = input("Enter Lender Name [e.g. HDFC Bank]: ").strip() or "HDFC Bank"
        
        income_str = input("Enter Monthly Net Salary (INR) [e.g. 50000]: ").strip()
        income = float(income_str) if income_str else 50000.0

        loan_str = input("Enter Eligible Loan Amount from Calculator (INR) [e.g. 1000000]: ").strip()
        loan = float(loan_str) if loan_str else 1000000.0

        rate_str = input("Enter Annual Interest Rate (%) [default 11.0]: ").strip()
        rate = float(rate_str) if rate_str else 11.0

        tenure_str = input("Enter Tenure in Months [default 60]: ").strip()
        tenure = int(tenure_str) if tenure_str else 60

        emi_str = input("Enter Existing Monthly EMIs (INR) [default 0]: ").strip()
        existing_emi = float(emi_str) if emi_str else 0.0

        analyze(lender, income, loan, rate, tenure, existing_emi)

if __name__ == "__main__":
    main()
