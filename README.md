# Superstore Business Analysis

> **A McKinsey-style Business Analysis Portfolio Project**  
> End-to-end data analysis pipeline: from raw data to actionable business recommendations

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-purple.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📊 Project Overview

This project delivers a **complete business analysis** of the Superstore retail dataset, following the same methodology used by McKinsey consultants and Google Data Analysts. It's designed as a **job-ready portfolio piece** for Data Analyst / Business Analyst / Operations Analyst positions.

### 🎯 Business Questions Answered

| # | Question | Answer |
|---|----------|--------|
| 1 | Is the business profitable? | **Yes — 12.47% net margin**, but with significant leakage |
| 2 | Where is money being lost? | **18.7% of transactions are unprofitable**, totaling **$156K in losses** |
| 3 | What drives losses? | **Deep discounting (>40%)** is the #1 profit killer (59.5% of loss transactions) |
| 4 | Which products perform best? | **Technology** category leads margins; **Office Supplies** leads volume |
| 5 | Does 80/20 rule apply? | **Yes** — a small subset of sub-categories drives the majority of revenue |
| 6 | Regional differences? | **West** region leads profit margins; **Central** lags behind |
| 7 | Customer segment insights? | **Consumer** is dominant (50.6% sales); **Home Office** has highest avg order value |

---

## 🏗️ Project Structure

```
project/
├── data/                    # Raw dataset (Superstore.csv)
├── src/                     # Core analysis modules
│   ├── data_loader.py       # Data loading & preprocessing
│   ├── data_quality.py      # Data quality assessment (6 checks)
│   ├── eda.py               # EDA engine (12 analysis dimensions)
│   ├── visualizer.py        # Plotly visualization engine (12 chart types)
│   └── insights.py          # Business insight generator (McKinsey-style)
├── utils/
│   └── helpers.py           # Pure Python utility functions (group-by, aggregation, etc.)
├── config/
│   └── settings.py          # Centralized configuration & color palette
├── images/                  # Exported charts (HTML/PNG)
├── main.py                  # Master pipeline orchestrator
├── notebook.ipynb           # Jupyter Notebook (complete walkthrough)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── portfolio.md             # Portfolio presentation page
├── resume.md                # Resume-ready project description
└── interview.md             # 20 interview questions with model answers
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd superstore-analysis

# 2. Install dependencies (minimal!)
pip install -r requirements.txt

# 3. Run the complete pipeline
python main.py

# 4. Export charts as HTML (optional)
python main.py --export
```

> **Note**: This project uses **pure Python** for data processing (no numpy/pandas required for core logic). Plotly is used for visualization. This design choice demonstrates deep Python fundamentals rather than just library usage.

---

## 📈 Analysis Pipeline (10 Steps)

### Step 1: Business Understanding 🏢
- Company profile, business model, stakeholder concerns
- KPI framework: Sales, Profit Margin, Discount Effectiveness, Customer Value

### Step 2: Data Understanding 🔍
- **9,994 transactions** across **13 columns**
- Data quality checks: missing values (0), duplicates (17), outliers (IQR method)
- **18.7% loss transactions** — identified as business-critical finding

### Step 3: Exploratory Data Analysis 📊
12 analysis dimensions covering:
- Sales & Profit overview
- Regional performance (4 regions)
- Category & Sub-category deep dive
- Customer segment analysis
- Discount impact assessment
- Pareto analysis (80/20 rule)
- Loss-maker identification
- Profit margin analysis

### Step 4: Business Insights 💡
9 actionable insights with McKinsey's "Insight → So What → Now What" framework

### Step 5: Dashboard Design 📋
Power BI dashboard blueprint with 3 pages, KPI cards, and interactive filters

---

## 🔑 Key Findings

### 💰 The Profit Leakage Problem

```
Total Sales:    $2,297,201
Total Profit:   $286,397   (12.47% margin)
Total Losses:   -$156,131  (from 18.7% of transactions)

→ Every $1 of profit is eroded by $0.55 of losses
→ Stopping just 30% of losses would increase overall profit by 16%
```

### 📉 Discount: The Silent Profit Killer

| Discount Level | Avg Margin | % of Orders |
|----------------|-----------|-------------|
| No Discount (0%) | +30.1% | 40% |
| Low (1-20%) | +13.2% | 38% |
| Medium (21-40%) | +0.3% | 13% |
| High (41-60%) | **-40.7%** | 6% |
| Very High (60%+) | **-122.6%** | 3% |

> **Insight**: Discounts above 40% destroy value. They should require manager approval.

### 📦 Loss-Making Sub-Categories

| Sub-Category | Total Loss | Primary Driver |
|-------------|-----------|----------------|
| Binders | -$38,510 | High discount + Low margin |
| Tables | -$32,412 | High discount (45% avg on losses) |
| Machines | -$30,119 | Deep discounting (70% avg) |
| Bookcases | -$12,152 | Discount + competitive pricing |
| Chairs | -$9,881 | Over-discounting |

---

## 🛠️ Technical Highlights

### Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Pure Python core** | Demonstrates CS fundamentals; no black-box dependencies |
| **Modular design** | `src/`, `utils/`, `config/` — enterprise-grade structure |
| **Plotly visualizations** | Interactive, publication-quality charts |
| **PEP 8 compliant** | Production-ready code style |
| **Function encapsulation** | Each analysis is a reusable, testable function |
| **Docstrings everywhere** | Professional documentation standard |

### Skills Demonstrated

```python
✅ Python (core):       csv, statistics, math, collections, argparse
✅ Data Manipulation:   group-by, aggregation, filtering, sorting
✅ Data Analysis:       descriptive stats, IQR, Pareto, margin analysis
✅ Visualization:       Plotly Graph Objects (12 chart types)
✅ Business Acumen:     KPI design, insight generation, recommendations
✅ Code Quality:        PEP 8, modular, documented, configurable
```

---

## 📊 Visualization Gallery

> 🎨 **[View All 12 Interactive Charts →](https://yaoyaojiahan.github.io/superstore-analysis/charts/)**  
> *GitHub Pages — click through to explore each chart with hover, zoom, and pan*

All charts are generated with Plotly and follow a **McKinsey-inspired corporate color palette**:

| # | Chart | Type | Business Question |
|---|-------|------|-------------------|
| 01 | Sales by Category | Treemap | Where does revenue come from? |
| 02 | Profit by Category | Waterfall | Which categories drive profit? |
| 03 | Category Comparison | Grouped Bar | Sales vs Profit by category |
| 04 | Sales by Sub-Category | Horizontal Bar | Top-selling product lines |
| 05 | Profit by Sub-Category | Horizontal Bar | Most profitable product lines |
| 06 | Regional Performance | Dual-Axis | Sales + Margin by region |
| 07 | Customer Segment | Donut | Who are our customers? |
| 08 | **Discount Impact** 🔴 | Bar | How discounts destroy margin |
| 09 | Pareto (80/20) | Bar + Line | Product concentration |
| 10 | Loss-Makers | Horizontal Bar | Which products lose money? |
| 11 | Shipping Mode | Donut | Logistics breakdown |
| 12 | Discount vs Profit | Scatter | Correlation analysis |

---

## 🎯 Target Job Keywords Alignment

This project is designed to demonstrate proficiency in:

| Keyword | How Demonstrated |
|---------|-----------------|
| **SQL** | Data aggregation, filtering, grouping logic (pure Python implementation) |
| **Excel** | KPI frameworks, conditional analysis, business reporting |
| **Python** | 500+ lines of production-quality Python code |
| **Power BI / Tableau** | Dashboard design section with detailed blueprint |
| **Statistical Analysis** | Descriptive stats, Pareto analysis, margin analysis, IQR outlier detection |
| **Business Analysis** | McKinsey-style insight generation & recommendations |

---

## 📝 Future Enhancements

- [ ] Time-series forecasting (Prophet / ARIMA)
- [ ] Customer segmentation (RFM analysis)
- [ ] SQL database integration (PostgreSQL)
- [ ] Real-time dashboard (Streamlit)
- [ ] Machine Learning: churn prediction, discount optimization

---

## 👤 Author

**Yao Jiahan**  
*Business Analyst | Data Analyst*  
Applied Statistics, B.Sc.

- **Specialization**: Business Analysis, Operations Analytics, AI + BA
- **Tools**: Python, Power BI, Excel, SQL
- **Domain Interest**: New Energy, AI-driven Analytics

---

## 📄 License

MIT License — Free to use for learning, portfolio, and professional development.

---

<p align="center">
  <b>⭐ If this project helps your job search, please star it on GitHub!</b>
</p>
