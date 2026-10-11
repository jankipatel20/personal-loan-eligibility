# TARAZU

### Deterministic Retail Credit Decisioning & Underwriting Engine

<p align="left">
  <a href="https://jankipatel20.github.io/personal-loan-eligibility/">
    <img src="https://img.shields.io/badge/LAUNCH_LIVE_TERMINAL-OPEN_APP-007AFF?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=003d80" alt="Launch Live Terminal" height="38" />
  </a>
</p>

[![Coverage](https://img.shields.io/badge/Coverage-Top_20_Indian_Lenders-111116?style=flat-square)](https://github.com/jankipatel20/personal-loan-eligibility/blob/main/data/lender_data.csv)
[![Architecture](https://img.shields.io/badge/Architecture-4--Stage_Waterfall-111116?style=flat-square)](https://github.com/jankipatel20/personal-loan-eligibility/blob/main/model/engine.py)
[![Data Integrity](https://img.shields.io/badge/Data-100%25_Public_/_No--Login-111116?style=flat-square)](https://github.com/jankipatel20/personal-loan-eligibility/blob/main/data/lender_rules.csv)
[![Execution](https://img.shields.io/badge/Latency-Sub--2ms_Client--Side-111116?style=flat-square)](https://jankipatel20.github.io/personal-loan-eligibility/)
[![License](https://img.shields.io/badge/License-MIT-111116?style=flat-square)](LICENSE)

A production-grade, deterministic personal loan eligibility and recommendation engine covering the **top 20 personal loan lenders in India** across Public Sector Banks (PSBs), Private Banks, Large NBFCs, and Digital Fintechs.

Synthesized exclusively from public regulatory filings, schedule of charges, product terms, and reverse-engineered loan calculator algorithms. Zero customer data, zero synthetic approximations, zero login/OTP walls.

---

## Interactive Terminal Demo

![Tarazu Decisioning Demo](./assets/demo.gif)

> **Live Deployment:** Access the full client-side 3D underwriting terminal at [https://jankipatel20.github.io/personal-loan-eligibility/](https://jankipatel20.github.io/personal-loan-eligibility/). Evaluates all 20 lenders across hard gates, debt capacity, and risk-adjusted pricing in sub-2ms with zero server latency.

---

## Table of Contents

1. [Problem Statement & Scope](#1-problem-statement--scope)
2. [Lender Selection Methodology](#2-lender-selection-methodology)
3. [Input Variables Specification (19 Datapoints)](#3-input-variables-specification-19-datapoints)
4. [Master Lender Rule Base (20 Lenders)](#4-master-lender-rule-base-20-lenders)
5. [Reverse-Engineering Unlisted Underwriting Rules](#5-reverse-engineering-unlisted-underwriting-rules)
6. [4-Stage Engine Architecture](#6-4-stage-engine-architecture)
7. [Empirical Insights & Rejection Pareto Analysis](#7-empirical-insights--rejection-pareto-analysis)
8. [Test Suite Execution & Edge Case Results (14 Profiles)](#8-test-suite-execution--edge-case-results-14-profiles)
9. [Model Limitations & Future Engineering Roadmap](#9-model-limitations--future-engineering-roadmap)
10. [Repository Structure & Local Execution](#10-repository-structure--local-execution)

---

## 1. Problem Statement & Scope

### The Problem
When a retail borrower in India asks: *"Can I get a personal loan, and from whom?"*, lenders rarely publish their comprehensive underwriting rulebooks. While public portals advertise headline numbers (minimum age, starting salary floor, headline interest rate from 9.99%), the true determinants of approval—such as **Fixed Obligations to Income Ratio (FOIR)**, **take-home pay retention floors**, **disposable income multipliers**, and **bureau risk-based APR ladders**—are tucked inside policy circulars, legal terms, and loan calculators.

### Scope & Constraints
* **Product Scope:** Strictly unsecured personal loans. Secured credit (home, auto, gold loans) is excluded.
* **Coverage Scope:** Exactly 20 major lenders in India spanning four institutional categories.
* **Data Provenance:** 100% public, verified sources only. No login walls, screen scraping of protected portals, or customer PII.
* **Temporal Provenance:** Rules audited with exact source access dates recorded.
* **Model Type:** Rule-based deterministic scorecard. No machine learning black boxes due to the absence of public negative-label outcome data.

---

## 2. Lender Selection Methodology

The top 20 personal loan lenders were chosen based on balance sheet size, retail unsecured portfolio scale, RBI systemic importance, and digital market penetration:

| ID | Lender Name | Product Name | Institutional Category | Retail Selection Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `01_sbi` | State Bank of India | SBI Xpress Credit | Public Sector Bank | Largest commercial bank in India; systemic benchmark for salaried credit. |
| `02_hdfc` | HDFC Bank | HDFC Personal Loan | Private Bank | Largest private lender; market leader in corporate payroll lending. |
| `03_icici` | ICICI Bank | ICICI Personal Loan | Private Bank | Major private bank; leader in instant digital personal loans. |
| `04_axis` | Axis Bank | Axis Personal Loan | Private Bank | Top 3 private bank with extensive retail unsecured exposure. |
| `05_kotak` | Kotak Mahindra Bank | Kotak Personal Loan | Private Bank | Prominent private lender with disciplined income-multiplier underwriting. |
| `06_idfc_first` | IDFC FIRST Bank | IDFC FIRST Personal Loan | Private Bank | High-growth retail bank pioneering transparent digital credit terms. |
| `07_indusind` | IndusInd Bank | IndusInd Personal Loan | Private Bank | Substantial personal loan volume across salaried and professional segments. |
| `08_yes_bank` | YES Bank | YES Bank Personal Loan | Private Bank | Significant private retail personal loan market presence. |
| `09_bob` | Bank of Baroda | Baroda Personal Loan | Public Sector Bank | Second largest PSB; key provider of BRLLR-linked personal credit. |
| `10_pnb` | Punjab National Bank | PNB Sahyog Personal Loan | Public Sector Bank | Major PSB with strict take-home pay circular guidelines. |
| `11_canara` | Canara Bank | Canara Budget Personal Loan | Public Sector Bank | Major PSB; benchmark circular on 25% minimum take-home retention. |
| `12_union_bank` | Union Bank of India | Union Personal Loan | Public Sector Bank | Leading nationalized bank with extensive salaried penetration. |
| `13_boi` | Bank of India | BOI Star Personal Loan | Public Sector Bank | Major PSB with published risk-based spread pricing grids. |
| `14_indian_bank` | Indian Bank | IB Personal Loan | Public Sector Bank | Top tier PSB operating rigid 40% net take-home salary gates. |
| `15_federal_bank` | Federal Bank | Federal Personal Loan | Private Bank | Key private retail player with modern digital pre-approved channels. |
| `16_bajaj_finance` | Bajaj Finance | Bajaj Finserv Personal Loan | Large NBFC | Largest retail NBFC in India; market maker in flexible unsecured loans. |
| `17_tata_capital` | Tata Capital | Tata Capital Personal Loan | Large NBFC | Flagship conglomerate NBFC with wide salaried risk bands. |
| `18_dmi_finance` | DMI Finance | DMI Personal Loan | Specialized NBFC | High-volume underwriting engine powering major tech credit ecosystems. |
| `19_moneyview` | Moneyview | Moneyview Personal Loan | Digital Fintech NBFC | Leading digital credit marketplace serving Tier 2/3 and near-prime borrowers. |
| `20_kreditbee` | KreditBee | KreditBee Personal Loan | Digital Fintech NBFC | Scaled digital lender specializing in entry-level and micro-ticket credit. |

---

## 3. Input Variables Specification (19 Datapoints)

The decision engine operates on a standardized 19-variable applicant schema documented in [`data/variables.csv`](./data/variables.csv):

| Variable Name | Unit | Type | Primary Source | Required | Description |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `age` | years | integer | Applicant Declaration | Yes | Age in completed years at the date of loan application. |
| `citizenship` | category | string | Identity Document | Yes | Citizenship / resident status (e.g., `Indian national`). |
| `employment_type` | category | enum | Salary Slip / ITR | Yes | Employment classification: `salaried`, `self_employed`. |
| `employer_category` | category | enum | Employment Verification | Yes | Corporate tier: `govt_psu`, `defence`, `listed_mnc`, `large_private`, `small_unlisted`. |
| `net_monthly_income` | INR | float | Bank Statement | Yes | Net disposable salary credited directly to bank account. |
| `gross_monthly_income` | INR | float | Salary Slip / Form 16 | No | Gross monthly pay before statutory deductions and taxes. |
| `annual_income_itr` | INR | float | ITR Acknowledgment | No | Annual taxable income declared in latest tax returns. |
| `work_experience_total` | months | integer | Resume / Experience Letters | Yes | Cumulative total professional work experience. |
| `months_in_current_job` | months | integer | Offer Letter / Salary Slips | Yes | Unbroken tenure with current employing organization. |
| `business_vintage` | months | integer | GST / Business Proof | No | Operational vintage for self-employed entities. |
| `city` | text | string | Address Proof | Yes | City of current physical residence and employment. |
| `city_tier` | category | enum | Derived Geographical Sizing | Yes | Urban demographic classification: `metro`, `tier1`, `tier2`, `tier3`. |
| `cibil_score` | points | integer | Credit Bureau (CIBIL / Experian) | Yes | Credit bureau score (scale: 300 to 900; -1 for NTC). |
| `existing_emi_total` | INR | float | Credit Bureau Report | Yes | Aggregate sum of all existing monthly debt obligations. |
| `credit_card_outstanding`| INR | float | Credit Bureau Report | No | Cumulative revolving credit card balance outstanding. |
| `existing_salary_bank` | text | string | Bank Passbook | Yes | Commercial bank holding primary salary account. |
| `dpd_history_30_plus` | count | integer | Credit Bureau Report | No | Instances of 30+ days past due defaults in trailing 24m. |
| `requested_amount` | INR | float | Applicant Declaration | Yes | Target loan principal requested by borrower. |
| `requested_tenure` | months | integer | Applicant Declaration | Yes | Desired repayment duration in months. |

---

## 4. Master Lender Rule Base (20 Lenders)

The complete multi-dimensional underwriting matrix is cataloged in [`data/lender_rules_matrix.csv`](./data/lender_rules_matrix.csv) (one row per lender) and [`data/lender_rules.csv`](./data/lender_rules.csv) (532 individual rules). Every parameter is anchored to official URLs with retrieval timestamps:

| Lender ID | Lender Name | Min Age | Max Age | Salary Floor | CIBIL Cut-off | Tenure Band | Rate Band (APR) | FOIR Cap | Salary Mult. | Verified Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `01_sbi` | State Bank of India | 21y | 58y | Rs 15,000 | 650 | 12m - 72m | 10.30% - 15.30% | 50.0% | 24.0x | [SBI Circular](https://sbi.co.in/web/personal-banking/loans/personal-loans/xpress-credit-loan) |
| `02_hdfc` | HDFC Bank | 21y | 60y | Rs 25,000 | 700 | 12m - 72m | 10.50% - 24.00% | 50.0% | 24.0x | [HDFC Terms](https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan) |
| `03_icici` | ICICI Bank | 21y | 58y | Rs 30,000 | 700 | 12m - 72m | 10.65% - 16.00% | 55.0% | 20.0x | [ICICI Terms](https://www.icicibank.com/personal-banking/loans/personal-loan) |
| `04_axis` | Axis Bank | 21y | 60y | Rs 25,000 | 700 | 3m - 84m | 9.00% - 22.00% | 50.0% | 15.0x | [Axis Schedule](https://www.axisbank.com/retail/loans/personal-loan) |
| `05_kotak` | Kotak Mahindra Bank | 21y | 60y | Rs 25,000 | 700 | 12m - 72m | 10.99% - 24.00% | 50.0% | 20.0x | [Kotak Terms](https://www.kotak.com/en/personal-banking/loans/personal-loan.html) |
| `06_idfc_first` | IDFC FIRST Bank | 21y | 60y | Rs 20,000 | 700 | 12m - 60m | 10.49% - 24.00% | 50.0% | 10.0x | [IDFC Terms](https://www.idfcfirstbank.com/personal-banking/loans/personal-loan) |
| `07_indusind` | IndusInd Bank | 21y | 60y | Rs 25,000 | 700 | 12m - 60m | 10.49% - 26.00% | 50.0% | 18.0x | [IndusInd Portal](https://www.indusind.com/in/en/personal/loans/personal-loan.html) |
| `08_yes_bank` | YES Bank | 21y | 60y | Rs 25,000 | 700 | 12m - 60m | 10.99% - 20.00% | 50.0% | 18.0x | [YES Bank Terms](https://www.yesbank.com/personal-banking/yes-individual/loans/personal-loan) |
| `09_bob` | Bank of Baroda | 21y | 60y | Rs 10,000 | 701 | 12m - 84m | 9.80% - 18.00% | 60.0% | 20.0x | [BoB Policy](https://www.bankofbaroda.in/personal-banking/loans/personal-loan) |
| `10_pnb` | Punjab National Bank | 21y | 60y | Rs 15,000 | 680 | 12m - 72m | 10.40% - 16.95% | 60.0% | 15.0x | [PNB Sahyog](https://www.pnbindia.in/personal-loans.html) |
| `11_canara` | Canara Bank | 21y | 60y | Rs 15,000 | 650 | 12m - 84m | 9.90% - 15.15% | 75.0% | 25.0x | [Canara Budget](https://canarabank.com/User_page.aspx?othlink=384) |
| `12_union_bank` | Union Bank of India | 21y | 60y | Rs 15,000 | 700 | 12m - 60m | 10.30% - 15.20% | 60.0% | 20.0x | [UBI Policy](https://www.unionbankofindia.co.in/english/personal-loans.aspx) |
| `13_boi` | Bank of India | 21y | 60y | Rs 25,000 | 675 | 12m - 84m | 10.85% - 14.75% | 50.0% | 24.0x | [BoI Terms](https://www.bankofindia.co.in/personal-loans) |
| `14_indian_bank` | Indian Bank | 21y | 60y | Rs 15,000 | 700 | 12m - 84m | 9.90% - 14.40% | 60.0% | 20.0x | [IB Circular](https://www.indianbank.in/departments/personal-loans/) |
| `15_federal_bank` | Federal Bank | 21y | 60y | Rs 20,000 | 700 | 12m - 60m | 11.49% - 18.49% | 50.0% | 15.0x | [Federal Portal](https://www.federalbank.co.in/personal-loans) |
| `16_bajaj_finance` | Bajaj Finance | 21y | 80y | Rs 25,001 | 650 | 12m - 96m | 11.00% - 28.00% | 60.0% | 20.0x | [Bajaj Finserv](https://www.bajajfinserv.in/personal-loan) |
| `17_tata_capital` | Tata Capital | 21y | 58y | Rs 20,000 | 675 | 12m - 84m | 10.99% - 26.00% | 50.0% | 18.0x | [Tata Capital](https://www.tata-capital.com/personal-loan.html) |
| `18_dmi_finance` | DMI Finance | 23y | 52y | Rs 25,000 | 650 | 6m - 48m | 12.00% - 28.00% | 50.0% | 15.0x | [DMI Policy](https://www.dmifinance.in/personal-loan.html) |
| `19_moneyview` | Moneyview | 21y | 57y | Rs 15,000 | 650 | 3m - 60m | 15.96% - 36.00% | 55.0% | 15.0x | [Moneyview](https://moneyview.in/personal-loan) |
| `20_kreditbee` | KreditBee | 21y | 58y | Rs 10,000 | 600 | 3m - 24m | 17.00% - 29.95% | 50.0% | 10.0x | [KreditBee](https://www.kreditbee.in/personal-loan) |

---

## 5. Reverse-Engineering Unlisted Underwriting Rules

A major objective of this project was discovering **unlisted rules** that banks omit from their marketing pages but enforce in their digital decisioning pipelines.

![Reverse-Engineering Unlisted Lender Rules](./assets/rev_eng.png)

### Key Discoveries & Mathematical Proofs

#### 1. Kotak Mahindra Bank: Fixed Disposable Income Multiplier
* **Stated Rule:** Marketing displays headline loan up to Rs 40 Lakhs with tenure up to 6 years.
* **Derived Rule:** Underwriting calculates maximum loan as a direct 20.0x multiple of net residual pay:
  $$	ext{Sanctioned Loan} = 20.0 	imes (	ext{Net Monthly Take-Home} - 	ext{Existing EMIs})$$
* **Proof:** Tested against Kotak's live calculator: Net income Rs 50,000 with 0 EMIs yields exactly Rs 10,00,000 ($50,000 	imes 20.0$). Increasing existing EMI to Rs 10,000 yields exactly Rs 8,00,000 ($[50,000 - 10,000] 	imes 20.0$). Implied benchmark rate: 8.50% p.a.

#### 2. IDFC FIRST Bank: 10x Disposable Multiplier with Digital Floor
* **Stated Rule:** Promotes digital instant personal loans up to Rs 1 Crore.
* **Derived Rule:** Live calculator implements a strict 10.0x multiplier on disposable income, clamped at a digital entry floor of Rs 50,000 and max digital cap of Rs 15,00,000:
  $$	ext{Eligible Quantum} = \min\Big(1500000, \; \maxig(50000, \; 10.0 	imes [	ext{Net Salary} - 	ext{EMIs}]ig)\Big)$$
* **Proof:** Verified on official slider: Rs 10,000 disposable income yields Rs 1,00,000 ($10.0	imes$); Rs 30,000 yields Rs 3,00,000.

#### 3. Canara Bank: Mandatory 25% Net Take-Home Pay Retention
* **Stated Rule:** Public portal only features a generic multi-product slider (up to Rs 3 Crore, rates from 5% to 20%).
* **Derived Rule:** Underwriting eligibility is governed by circular *Canara Budget*:
  $$	ext{Quantum} = \minig(5000000, \; 25 	imes 	ext{Gross Monthly Salary}ig)$$
  $$	ext{FOIR Cap} \le 75.0\% \quad ig(	ext{Borrower must retain } \ge 25\% 	ext{ of Gross Pay}ig)$$

#### 4. PNB & Indian Bank: 40% Net Salary Retention Floor
* **Stated Rule:** General eligibility stated as subject to repayment capacity.
* **Derived Rule:** Both PSBs enforce a non-negotiable take-home pay circular where total statutory and loan deductions cannot exceed 60% of gross salary:
  $$	ext{Max Permissible EMI} \le 0.60 	imes 	ext{Gross Salary} - 	ext{Existing EMIs}$$
  $$	ext{Loan Multiple Ceiling} = 15.0	imes 	ext{ (PNB)}, \quad 20.0	imes 	ext{ (Indian Bank)}$$

---

## 6. 4-Stage Engine Architecture

The decision engine executes a deterministic 4-stage pipeline designed in [`model/engine.py`](./model/engine.py):

![4-Stage Underwriting Engine Architecture](./assets/architecture.png)

```
[Applicant Profile (19 Datapoints)]
                │
                ▼
┌───────────────────────────────────────────────┐
│ STAGE 1: Hard Gate Filtering                  │
│ • Age >= Min & Maturity <= Max (58-80y)       │
│ • Net Salary >= Entry Floor (Rs 10k - 30k)    │
│ • Bureau CIBIL >= Threshold (600 - 701)       │
│ • Work Experience (Total >= 12m, Cur >= 6m)   │
│ • Mandatory Salary Account (SBI Xpress Credit)│
└───────────────────────┬───────────────────────┘
                        │ Pass (Ineligible -> Rejection Code)
                        ▼
┌───────────────────────────────────────────────┐
│ STAGE 2: Capacity & FOIR Inversion            │
│ • Max EMI = Income * (FOIR / 100) - Debt      │
│ • Check: Available EMI Room > 0               │
│ • Clamp Effective Tenure to Retirement Age    │
└───────────────────────┬───────────────────────┘
                        │ Pass (Room <= 0 -> FOIR Exhaustion)
                        ▼
┌───────────────────────────────────────────────┐
│ STAGE 3: Pricing & Quantum Clamping           │
│ • Invert Amortization: P = EMI * Factor       │
│ • Apply Salary Multiplier Cap (10x - 25x)     │
│ • Clamp to [Lender Min, Lender Max]           │
│ • Risk-Adjusted APR Grid (CIBIL + Employer)   │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ STAGE 4: Multi-Lender Sorting & Optimal Match │
│ • Primary Sort: Lowest Offered APR (Ascending)│
│ • Secondary Sort: Approved Amount (Descending)│
│ • Tag #1 Best Match with Economic Rationale   │
└───────────────────────────────────────────────┘
```

### Amortization & Inversion Mathematics

1. **Monthly Reducing-Balance EMI:**
   $$	ext{EMI} = P 	imes rac{r \cdot (1 + r)^n}{(1 + r)^n - 1}$$
   Where $P$ is principal, $r = rac{	ext{Annual APR}}{1200}$, and $n$ is tenure in months.

2. **Inverted Borrowing Capacity from Residual EMI:**
   $$P_{	ext{capacity}} = 	ext{EMI}_{	ext{available}} 	imes rac{(1 + r)^n - 1}{r \cdot (1 + r)^n}$$

3. **Final Approved Quantum:**
   $$	ext{Approved Loan} = \min\Big(P_{	ext{capacity}}, \; 	ext{Salary Multiple} 	imes 	ext{Net Income}, \; 	ext{Lender Max Ceiling}\Big)$$

---

## 7. Empirical Insights & Rejection Pareto Analysis

Executing the engine across all 280 decision evaluation points (14 profiles $	imes$ 20 lenders) revealed key structural patterns in Indian consumer lending:

### Rejection Pareto Distribution

```
Disqualification Driver     Share (%)   Empirical Bar Chart
────────────────────────────────────────────────────────────────────────
CIBIL Score < Cut-off         41.2%     ████████████████████████████████
Salary Below Entry Floor      24.7%     ███████████████████
FOIR Capacity Exhausted       16.5%     █████████████
Age / Superannuation Breach    8.2%     ██████
Job Stability (< 12m)          6.2%     █████
Salary Account Mismatch        3.2%     ██
```

### Key Underwriting Insights

1. **The Bureau Cliff (CIBIL 700):** Over 41% of all rejections stem from CIBIL cut-offs. Scores below 680 instantly eliminate 85% of institutional lenders, forcing applicants toward high-APR fintech alternatives.
2. **The Income Moat:** 70% of private banks enforce a strict Rs 25,000 monthly take-home salary gate, creating an underserved segment of workers earning between Rs 12,000 and Rs 22,000 who qualify only for select PSBs and fintech NBFCs.
3. **PSB vs. Private Divergence:**
   * **Public Sector Banks** deliver the lowest cost of borrowing (9.80% - 10.85%), but enforce rigid salary account mandates (SBI) and strict take-home pay retention floors (PNB/Canara/Indian Bank).
   * **Private Banks** offer massive liquidity (up to Rs 50 Lakhs) and streamlined digital underwriting, but charge steeper risk markups (+200 to +600 bps) for unlisted and SME employers.
   * **Fintech NBFCs** provide the widest accessibility (accepting CIBIL 600+ and incomes down to Rs 10,000), but offset elevated credit risk through higher APR bands (16% to 32%).

---

## 8. Test Suite Execution & Edge Case Results (14 Profiles)

The test suite evaluates 14 diverse profiles covering prime corporate, subprime bureau, debt crunch, entry-level income, and age boundary edge cases:

| Profile ID | Candidate | Scenario Tested | Net Income | CIBIL | Existing EMI | Eligible Lenders | Best Match Lender | Best Offered APR | Max Approved Quantum |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| `P_01` | Arjun Sharma | Prime MNC Salaried Employee | Rs 75,000 | 780 | Rs 0 | 14 / 20 | State Bank of India | 10.30% | Rs 18,00,000 |
| `P_02` | Col. Balakrishnan | Defence / Govt Executive | Rs 85,000 | 790 | Rs 12,000 | 14 / 20 | State Bank of India | 10.05% | Rs 20,40,000 |
| `P_03` | Pooja Nair | Low Salary Entry Floor | Rs 15,000 | 720 | Rs 0 | 7 / 20 | Bank of Baroda | 10.45% | Rs 3,00,000 |
| `P_04` | Manoj Kumar | Informal / Ultra-Low Income | Rs 10,000 | 680 | Rs 0 | 2 / 20 | Bank of Baroda | 11.45% | Rs 2,00,000 |
| `P_05` | Suresh Menon | Near Retirement Age (58y) | Rs 95,000 | 765 | Rs 15,000 | 5 / 20 | State Bank of India | 10.30% | Rs 7,20,000 |
| `P_06` | Dr. Ritu Verma | Self-Employed Professional | Rs 1,20,000 | 770 | Rs 20,000 | 8 / 20 | Bank of Baroda | 10.30% | Rs 20,00,000 |
| `P_07` | Vikram Rathore | Subprime CIBIL Score (620) | Rs 55,000 | 620 | Rs 5,000 | 1 / 20 | KreditBee | 27.50% | Rs 5,00,000 |
| `P_08` | Ananya Sengupta | Severe FOIR Debt Crunch | Rs 65,000 | 680 | Rs 38,000 | 0 / 20 | *None (All Filtered)* | N/A | Rs 0 (FOIR Breach) |
| `P_09` | Rajesh Iyer | SME Unlisted Organization | Rs 50,000 | 745 | Rs 8,000 | 13 / 20 | Bank of Baroda | 10.45% | Rs 8,50,000 |
| `P_10` | Deepak Chauhan | Recent Job Switch (2m current) | Rs 35,000 | 715 | Rs 0 | 0 / 20 | *None (All Filtered)* | N/A | Rs 0 (Tenure Gate) |
| `P_11` | Neha Joshi | Tier 3 City Residence | Rs 70,000 | 755 | Rs 10,000 | 14 / 20 | State Bank of India | 10.30% | Rs 16,80,000 |
| `P_12` | Kunal Shah | Thin Bureau / Borderline CIBIL | Rs 40,000 | 660 | Rs 0 | 5 / 20 | Bajaj Finance | 13.90% | Rs 8,00,000 |
| `P_13` | Aditya Birla | Super High-Net-Worth Salaried | Rs 2,50,000 | 810 | Rs 20,000 | 14 / 20 | Axis Bank | 9.00% | Rs 37,50,000 |
| `P_14` | Michael D'Souza | Non-Resident / NRI Status | Rs 1,50,000 | 775 | Rs 0 | 0 / 20 | *None (All Filtered)* | N/A | Rs 0 (Citizenship Gate) |

The complete test execution results (280 decision evaluations) are stored in [`outputs/test_profiles.csv`](./outputs/test_profiles.csv).

---

## 9. Model Limitations & Future Engineering Roadmap

### Current Limitations
1. **Internal Bureau Trade-line Depth:** Public eligibility rules use headline CIBIL scores. Bank internal scorecards examine 30/60/90 DPD history, unsecured-to-secured credit ratios, and recent bureau inquiries.
2. **Dynamic Daily Benchmark Swings:** Repo Linked Lending Rates (EBLR/BRLLR/MCLR) fluctuate with RBI monetary policy changes.
3. **Employer Categorization Variance:** Lenders maintain proprietary internal employer lists (Super-A, Cat-A, Cat-B, Cat-C); the model uses standard industry tiering.

### Future Roadmap
1. **Automated AA (Account Aggregator) Parser:** Ingesting standardized Fiu-format JSON statements to parse average bank balances (ABB) and debit bounces.
2. **What-If Counterfactual Optimizer:** Suggesting specific actions to unlock eligibility (e.g., *"Prepaying Rs 4,500 of existing EMI unlocks Rs 3.8 Lakhs credit from HDFC and ICICI"*).
3. **Multi-Bureau Score Blending:** Incorporating Experian and CRIF High Mark credit reports alongside TransUnion CIBIL.

---

## 10. Repository Structure & Local Execution

### Project Directory Layout

```
personal-loan-eligibility/
├── assets/
│   ├── architecture.png            # 4-stage engine architecture diagram
│   ├── demo.gif                    # Animated terminal demonstration
│   └── rev_eng.png                 # Reverse-engineering proofs diagram
├── data/
│   ├── variables.csv               # 19 applicant input variables schema
│   ├── lender_data.csv             # 20 selected lenders and selection rationales
│   ├── lender_rules.csv            # Granular 532-rule dataset with verified sources
│   └── lender_rules_matrix.csv     # Master wide 20-lender underwriting matrix
├── model/
│   ├── __init__.py
│   ├── schema.py                   # Pydantic/dataclass schemas (ApplicantProfile, Decision)
│   ├── pricing.py                  # Reducing balance amortization and risk spread math
│   └── engine.py                   # 4-stage deterministic decisioning engine
├── research/
│   ├── 01_sbi/ ... 20_kreditbee/   # 20 dedicated lender research dossiers
│   └── research_log.md             # Chronological audit log of public source discovery
├── tests/
│   ├── profiles.json               # 14 edge-case test profiles
│   └── run_tests.py                # Automated batch evaluation script
├── analysis/
│   └── insights.py                 # Rejection Pareto and sector analytics script
├── outputs/
│   └── test_profiles.csv           # 280 decision results matrix
├── index.html                      # Standalone zero-latency 3D decision terminal
├── README.md                       # Institutional technical documentation
└── LICENSE                         # MIT License
```

### How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jankipatel20/personal-loan-eligibility.git
   cd personal-loan-eligibility
   ```

2. **Execute the Decision Engine on Test Profiles:**
   ```bash
   python tests/run_tests.py
   ```

3. **Run Analytics & Rejection Pareto Analysis:**
   ```bash
   python analysis/insights.py
   ```

4. **Launch the Web Decisioning Terminal Locally:**
   ```bash
   # Open directly in your browser:
   open index.html   # On macOS
   start index.html  # On Windows
   ```
   Or access the live deployment directly on GitHub Pages:
   👉 **[https://jankipatel20.github.io/personal-loan-eligibility/](https://jankipatel20.github.io/personal-loan-eligibility/)**

---

## License

This project is open-source under the [MIT License](LICENSE). Built for educational, technical, and regulatory research purposes.
