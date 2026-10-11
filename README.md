# Personal Loan Eligibility & Recommendation Engine (India)

A production-grade, deterministic eligibility and underwriting recommendation engine covering the **top 20 personal loan lenders in India** across Public Sector Banks (PSBs), Private Banks, Large NBFCs, and Digital Fintechs.

Built with **100% publicly sourced, verified, no-login data** from official bank portals, regulatory Key Fact Statements (KFS), scheme circulars, and live reverse-engineered calculators.

---

## Table of Contents
1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [Lender Shortlist & Selection Methodology](#2-lender-shortlist--selection-methodology)
3. [Input Variables Schema (19 Variables)](#3-input-variables-schema-19-variables)
4. [Master Rules Dataset & Integrity Audit](#4-master-rules-dataset--integrity-audit)
5. [Reverse-Engineering Unlisted Rules](#5-reverse-engineering-unlisted-rules)
6. [4-Stage Engine Architecture](#6-4-stage-engine-architecture)
7. [Test Suite & Edge Case Results (14 Profiles)](#7-test-suite--edge-case-results-14-profiles)
8. [Analytical Insights & Sector Comparisons](#8-analytical-insights--sector-comparisons)
9. [Limitations & Intellectual Honesty](#9-limitations--intellectual-honesty)
10. [How to Run](#10-how-to-run)

---

## 1. Executive Summary & Problem Statement

### The Problem
When an individual in India asks: *"Can I get a personal loan, for how much, and from whom?"*, marketing pages offer misleading generic headlines (e.g. *"Loans up to ₹50 Lakhs at 10.5%"*). In reality, personal loan underwriting is governed by two layers of rules:
1. **Listed Rules**: Stated minimum age, basic salary floors, and entry CIBIL cutoffs.
2. **Unlisted / Hidden Rules**: Fixed Obligation to Income Ratio (**FOIR / DTI** caps), **Salary Multiplier Caps** ($N 	imes 	ext{Salary}$), **Age at Maturity Caps** (superannuation cutoff), and **Employer Categorization Tiers** (Category A/B/C/D).

### The Solution
This repository collects **532 verified underwriting rules** across India's top 20 lenders, defines **19 standardized applicant variables**, provides empirical mathematical proofs for hidden rules, and builds a **4-stage deterministic decision engine** that evaluates applicants, enforces debt capacity, clamps loan quantums, prices risk spreads, and ranks eligible lenders to identify the **#1 Best Match**.

---

## 2. Lender Shortlist & Selection Methodology

The top 20 lenders were selected based on **unsecured retail credit book size**, **market share**, and **underwriting segment diversity**:

| # | Lender | Category | Rationale / Market Signal | Primary Focus |
|---|---|---|---|---|
| 1 | **State Bank of India (SBI)** | Public Sector Bank | India's largest bank; dominant retail personal loan book (Xpress Credit) | Prime Salaried, Govt, Defence |
| 2 | **Bank of Baroda (BoB)** | Public Sector Bank | 2nd largest PSB; accessible ₹10k salary floor, up to 84m tenure | Salaried & Professionals |
| 3 | **Punjab National Bank (PNB)** | Public Sector Bank | 3rd largest PSB; published $15	imes$ gross salary formula, 40% NTH floor | Salaried, Semi-urban |
| 4 | **Canara Bank** | Public Sector Bank | Major PSB; Canara Budget scheme ($25	imes$ salary, 25% NTH / 75% FOIR cap) | Govt, PSU, Reputed Corporate |
| 5 | **Union Bank of India** | Public Sector Bank | Leading PSB; published EBLR rate matrix (from 9.30%), min age 18 | Salaried, Corporate Tie-up |
| 6 | **Bank of India (BoI)** | Public Sector Bank | Leading PSB; Star Suvidha Express ($24	imes$ salary, up to 84m tenure) | Salaried & Pensioners |
| 7 | **Indian Bank** | Public Sector Bank | Leading PSB; IB Clean Loan ($20	imes$ salary, 40% mandatory take-home pay) | Confirmed Corporate Salaried |
| 8 | **HDFC Bank** | Private Bank | #1 private retail lender; benchmark prime corporate underwriting | Super-A MNCs, Tier-1 Salaried |
| 9 | **ICICI Bank** | Private Bank | #2 private bank; ₹30k strict salary gate, Super-A / Defence multipliers | Prime Salaried |
| 10 | **Axis Bank** | Private Bank | #3 private bank; proven $15.0	imes$ baseline multiplier (~32% baseline FOIR) | Salaried (ETB & NTB) |
| 11 | **Kotak Mahindra Bank** | Private Bank | Top private bank; proven formula $	ext{Loan} = 20	imes(	ext{Income}-	ext{Obligations})$ | Prime Corporate Salaried |
| 12 | **IndusInd Bank** | Private Bank | Major private bank; published 50% DTI benchmark, reducing balance schedule | Corporate Salaried |
| 13 | **IDFC FIRST Bank** | Private Bank | Pioneer in zero-foreclosure digital loans; proven $10	imes$ net multiplier | Digital Prime Salaried |
| 14 | **Yes Bank** | Private Bank | Fast private retail lender; 10%–21% rate ceiling, tiered foreclosure | Corporate Salaried |
| 15 | **Federal Bank** | Private Bank | Premier private bank; FedPremia scheme (₹25k min salary, 21–55 age cap) | Salaried (South & Metro) |
| 16 | **Bajaj Finance** | Large NBFC | India's largest consumer NBFC; ₹55L quantum cap, age up to 80 years | Broad Salaried & Self-Employed |
| 17 | **Tata Capital** | Large NBFC | Leading diversified NBFC; published $30	imes$ monthly salary multiplier | Salaried (Prime & Near-Prime) |
| 18 | **DMI Finance** | Large NBFC | Major digital NBFC; strict 23–52 age demographic gate, ₹10L digital cap | Digital Salaried & Gig Workers |
| 19 | **Moneyview** | Fintech / NBFC | Leading digital fintech; ₹25k in-hand bank credit mandatory, 21–57 age | Digital Underbanked Salaried |
| 20 | **KreditBee** | Fintech / NBFC | Top digital micro-lender; ₹10k lowest market entry floor, 600+ CIBIL | Entry-level & Thin-file Salaried |

---

## 3. Input Variables Schema (19 Variables)

Defined in [`data/variables.csv`](file:///D:/personal-loan-eligibility/data/variables.csv):

| Variable Name | Unit | Type | Source | Required | Description |
|---|---|---|---|---|---|
| `age` | years | int | applicant | Yes | Applicant current age at application |
| `citizenship` | category | string | applicant | Yes | Citizenship/residency status (e.g. Indian national) |
| `employment_type` | category | enum | applicant | Yes | `salaried`, `self_employed_professional`, `self_employed_business`, `pensioner` |
| `employer_category` | category | enum | document | Yes | `govt_psu`, `defence`, `listed_mnc`, `large_private`, `small_unlisted` |
| `net_monthly_income` | INR | float | document | Yes | Verified take-home monthly salary credited to bank |
| `gross_monthly_income` | INR | float | document | No | Gross monthly salary before tax deductions |
| `annual_income_itr` | INR | float | document | No | Annual taxable income declared in ITR |
| `work_experience_total` | months | int | document | Yes | Total cumulative career experience across all employers |
| `months_in_current_job`| months | int | document | Yes | Continuous service tenure with present employer |
| `business_vintage` | months | int | document | No | Operational vintage in months (self-employed only) |
| `city` | text | string | applicant | Yes | Current city of residence / employment |
| `city_tier` | category | enum | derived | Yes | `metro`, `tier1`, `tier2`, `tier3` |
| `cibil_score` | points | int | bureau | Yes | Bureau credit score (-1 for no history, else 300–900) |
| `existing_emi_total` | INR/month| float | bureau | Yes | Sum of all active monthly EMIs currently serviced |
| `recent_enquiries_6m` | count | int | bureau | No | Number of hard credit inquiries in last 6 months |
| `past_delays_flag` | boolean | boolean | bureau | No | Indicator of 30+ DPD defaults or write-offs in last 24m |
| `requested_amount` | INR | float | applicant | Yes | Desired principal personal loan amount |
| `requested_tenure` | months | int | applicant | Yes | Desired loan repayment tenure in months |
| `existing_salary_bank` | text | string | document | Yes | Primary bank holding applicant salary account |

---

## 4. Master Rules Dataset & Integrity Audit

The master rules dataset ([`data/lender_rules.csv`](file:///D:/personal-loan-eligibility/data/lender_rules.csv)) contains **532 verified underwriting rules**:
- **100% Official Bank Domains**: Every URL points directly to verified official bank/NBFC domains (e.g., `sbi.co.in`, `hdfcbank.com`, `bankofbaroda.in`, `canarabank.com`, `bajajfinserv.in`).
- **Listed Rules (497 rules — 93.4%)**: Stated policies with verbatim `raw_quote` extracts.
- **Unlisted Rules (35 rules — 6.6%)**: Hidden underwriting levers marked with `is_estimate: yes`, `source_type: derived`, accompanied by full mathematical derivation explanations.

---

## 5. Reverse-Engineering Unlisted Rules

### Mathematical Proofs of Hidden Levers:

1. **Kotak Mahindra Bank ($	ext{Loan} = 20	imes	ext{Disposable Income}$)**:
   - On Kotak's live public calculator:
     - Salary ₹50,000 with ₹10,000 obligations $ightarrow$ Output = **₹8,00,000** ($20 	imes 40,000$).
     - Salary ₹50,000 with ₹0 obligations $ightarrow$ Output = **₹10,00,000** ($20 	imes 50,000$).
   - Solved internal benchmark interest rate: **8.50% p.a.**

2. **IDFC FIRST Bank ($	ext{Loan} = 10	imes	ext{Disposable Income}$)**:
   - On IDFC's live calculator:
     - Clamping floor: When Income = Obligations (₹75k - ₹75k = 0), the output clamps to **₹50,000**.
     - Clamping ceiling: Incomes of ₹2,00,000 and ₹3,00,000 both produce **₹15,00,000** (hard digital cap).

3. **Canara Bank (75.0% FOIR Capacity)**:
   - Canara Budget circular explicitly mandates: *"Minimum net take-home pay must not be less than 25% of gross salary or ₹10,000/month after all EMIs."*
   - Implied maximum debt capacity: $100\% - 25\% =$ **75.0% FOIR**.

4. **Punjab National Bank & Indian Bank (60.0% FOIR Capacity)**:
   - Both banks mandate that Net Take-Home Pay (NTHP) cannot fall below 40% of gross salary.
   - Implied maximum debt capacity: $100\% - 40\% =$ **60.0% FOIR**.

5. **Axis Bank ($15.0	imes$ Baseline Multiplier)**:
   - Net Monthly Income ₹50,000 with ₹0 obligations yields exactly **₹7,50,000** ($15.0	imes$ multiple).
   - Implied baseline FOIR at 9.99% for 60m is **31.86%**, stretching to 50% max capacity.

---

## 6. 4-Stage Engine Architecture

Implemented across [`model/schema.py`](file:///D:/personal-loan-eligibility/model/schema.py), [`model/pricing.py`](file:///D:/personal-loan-eligibility/model/pricing.py), and [`model/engine.py`](file:///D:/personal-loan-eligibility/model/engine.py):

### Stage 1: Hard Eligibility Gates
Filters applicant against hard hurdles:
- Nationality check (`Indian national`)
- Age bounds (`min_age <= age <= max_age_application`)
- Retirement cap check (`age + (tenure/12) <= max_age_maturity`)
- Minimum net monthly salary gate (`salary >= min_salary`)
- Minimum bureau credit score (`cibil >= min_cibil`)
- Work stability (`total_exp >= min_total_exp` and `current_job >= min_current_job`)
- Mandatory salary account requirements (e.g. SBI/Canara salary mandate)

### Stage 2: Debt Service Capacity (FOIR & Multipliers)
Computes permissible monthly borrowing capacity:
$$	ext{Max Permissible EMI Room} = (	ext{Net Monthly Salary} 	imes 	ext{FOIR Cap}) - 	ext{Existing EMIs}$$
If $	ext{EMI Room} \le 0$, application is declined for **FOIR breach**.

### Stage 3: Risk-Based Pricing & Quantum Clamping
- **Pricing Scorecard**: Places applicant in the lender's published rate band based on bureau score (780+, 750+, 700+, 650+) and employer tier (Defence/Govt discount, MNC neutral, unlisted spread).
- **Quantum from EMI**:
  $$	ext{Capacity}_{	ext{EMI}} = 	ext{EMI Room} 	imes rac{(1 + r_m)^n - 1}{r_m (1 + r_m)^n}$$
  where $r_m = 	ext{rate}/1200$, $n = 	ext{effective tenure in months}$.
- **Multiplier Cap**: $	ext{Capacity}_{	ext{Mult}} = 	ext{Salary Multiplier} 	imes 	ext{Monthly Salary}$.
- **Final Sanctioned Quantum**:
  $$	ext{Eligible Quantum} = \min(	ext{Capacity}_{	ext{EMI}}, 	ext{Capacity}_{	ext{Mult}}, 	ext{Lender Max Limit})$$
  Clamped above the lender's minimum ticket size.

### Stage 4: Ranking & "Best Match" Recommendation
Eligible lenders are ranked:
1. **Primary**: Lowest offered interest rate (cheapest borrowing cost).
2. **Secondary**: Highest eligible loan amount.
3. **Tertiary**: Lowest processing fee.

---

## 7. Test Suite & Edge Case Results (14 Profiles)

14 edge cases evaluated across all 20 lenders (**280 decisions**) in [`outputs/test_profiles.csv`](file:///D:/personal-loan-eligibility/outputs/test_profiles.csv):

| Profile ID | Applicant Name | Key Demographics | Test Scenario / Edge Case | Approvals | Best Match Lender | Best Rate | Approved EMI |
|---|---|---|---|:---:|---|:---:|:---:|
| `P_01` | Arjun Sharma | 29y, ₹75k Sal, 780 CIBIL | Prime Young Salaried MNC Employee | **19 / 20** | Axis Bank | 9.00% | ₹10,379 |
| `P_02` | Col. Rajesh Verma | 35y, ₹85k Sal, 790 CIBIL | Defence Package: Lowest Spread | **19 / 20** | Axis Bank | 9.00% | ₹20,758 |
| `P_03` | Pooja Verma | 23y, ₹15k Sal, 720 CIBIL | Low Income Gate (Fails ₹25k/₹30k gates) | **10 / 20** | Union Bank of India | 10.80% | ₹4,897 |
| `P_04` | Manoj Kumar | 22y, ₹10k Sal, 680 CIBIL | Absolute Floor: Fails all standard banks | **1 / 20** | KreditBee | 26.37% | ₹2,703 |
| `P_05` | Suresh Nair | 58y, ₹95k Sal, 765 CIBIL | Age at Maturity: 58yo applying for 5y | **16 / 20** | Union Bank of India | 9.47% | ₹27,540 |
| `P_06` | Dr. Ramesh Gupta | 62y, ₹1.2L Sal, 770 CIBIL | Senior Borrower: Exceeds age 60 bank cap | **0 / 20** | *Ineligible across standard salaried* | N/A | N/A |
| `P_07` | Vikram Singh | 31y, ₹55k Sal, 620 CIBIL | Subprime Bureau: CIBIL 620 fails 650/700 | **1 / 20** | KreditBee | 29.45% | ₹12,645 |
| `P_08` | Ananya Joshi | 27y, ₹65k Sal, 680 CIBIL | Bureau Boundary: CIBIL 680 fails 700 gate | **8 / 20** | Union Bank of India | 12.94% | ₹10,719 |
| `P_09` | Rajesh Kumar | 34y, ₹50k Sal, ₹28k EMI | FOIR Stress: Existing EMIs exhaust 50% DTI | **4 / 20** | Indian Bank (60% FOIR) | 11.60% | ₹2,000 |
| `P_10` | Deepak Yadav | 28y, ₹35k Sal, 715 CIBIL | Employer Tier: Small Unlisted Firm | **17 / 20** | Union Bank of India | 12.24% | ₹8,332 |
| `P_11` | Neha Kulkarni | 26y, ₹70k Sal, 3m in job | Current Job Vintage: 3m fails 6m gate | **0 / 20** | *Ineligible across all lenders* | N/A | N/A |
| `P_12` | Kunal Sen | 22y, ₹40k Sal, 6m total exp | Career Vintage: 6m fails 12m career gate | **0 / 20** | *Ineligible across all lenders* | N/A | N/A |
| `P_13` | Aditya Singhania | 38y, ₹2.5L Sal, ₹30L Loan | High Net Worth: ₹30L large ticket test | **19 / 20** | Axis Bank | 9.00% | ₹62,275 |
| `P_14` | Michael Roberts | 33y, British Expat | Non-Indian Citizen: Expat hard gate | **0 / 20** | *Ineligible across all lenders* | N/A | N/A |

---

## 8. Analytical Insights & Sector Comparisons

Generated via [`analysis/insights.py`](file:///D:/personal-loan-eligibility/analysis/insights.py):

### 1. Hard Gate Rejection Pareto Analysis
Which underwriting rules trigger the most rejections across diverse applicants?

```
Employment Vintage / Stability    ████████████████████  25.9% (57 declines)
Age Bounds / Superannuation Cap   ████████████████      20.9% (46 declines)
Credit Score / Bureau Cutoff      ███████████████       19.1% (42 declines)
Minimum Salary Gate Breach        █████████             12.3% (27 declines)
Citizenship / Non-Resident Gate   ███████                9.1% (20 declines)
Capacity / Minimum Loan Size      █████                  6.8% (15 declines)
Mandatory Salary Account          ████                   5.9% (13 declines)
```

### 2. Sector Underwriting Comparison
| Sector | Approval Rate | Mean Offered Rate | Mean Eligible Loan | Best Matches Won |
|---|:---:|:---:|:---:|:---:|
| **Public Sector Banks (PSBs)** | 43.9% | **11.53%** | ₹12,73,500 | **5** (Lowest rates for prime/govt) |
| **Private Banks** | 35.7% | **11.82%** | **₹16,96,507** | **3** (High quantum for prime MNCs) |
| **Large NBFCs** | 46.4% | **14.65%** | ₹15,98,765 | **0** (Flexible age up to 80y, high ticket) |
| **Digital Fintechs** | **50.0%** | **20.90%** | ₹5,45,306 | **2** (Micro-incomes & sub-650 CIBIL) |

### 3. CIBIL Score vs Risk Spread Sensitivity
| CIBIL Score | Eligible Lenders | Lowest Available Rate | Median Available Rate | Highest Rate |
|---|:---:|:---:|:---:|:---:|
| **620** | 1 (Fintech only) | 29.45% | 29.45% | 29.45% |
| **680** | 9 | 12.94% | 21.50% | 30.00% |
| **720** | 10 | 10.80% | 13.32% | 19.69% |
| **765** | 16 | 9.47% | 10.95% | 16.87% |
| **780+** | **19** | **9.00%** | **10.50%** | **16.00%** |

---

## 9. Limitations & Intellectual Honesty

1. **Estimated Multipliers & FOIR**: While FOIR limits for PNB (60%), Indian Bank (60%), and Canara Bank (75%) are derived directly from published take-home pay rules, internal bank credit committees may apply discretionary hair-cuts based on employer category.
2. **Dynamic Bureau Spread Tables**: Benchmark rates (Repo, RLLR, EBLR, MCLR) are updated periodically by lenders. Spreads recorded reflect published schedules as of October 2026.
3. **No Bureau Tradeline Visibility**: Real underwriting checks DP-30/60 history and unsecured credit utilization ratios. The model accepts self-reported bureau scores and clean delinquency flags.
4. **Pre-Approved Offers vs Open-Market Applications**: Pre-approved existing salary account holders frequently receive waivers on processing fees and instant digital disbursements not available to walk-in applicants.

---

## 10. How to Run

To run the complete pipeline from scratch:

```bash
# 1. Run the test suite across all 14 profiles (populates outputs/test_profiles.csv)
python tests/run_tests.py

# 2. Run the analytical insights and sector comparisons
python analysis/insights.py

# 3. Audit master rules dataset integrity
python scratch/test_rules_integrity.py
```
