# 🍬 Nassau Candy Distributor — Product Profitability Analysis

A data-driven analysis of product line profitability and margin performance for Nassau Candy Distributor, built for Unified Mentor Pvt. Ltd. Includes end-to-end EDA, a research paper, and an interactive Streamlit dashboard.

## 📌 Problem Statement

Sales volume alone is misleading for a distributor. This project answers:
- Which products truly drive profit vs. which just drive sales volume?
- How does profitability vary across product divisions (Chocolate / Sugar / Other)?
- Is the business over-dependent on a small set of products?
- Which products or factories need pricing/cost intervention?

## 📂 Repository Structure

```
nassau-candy-dashboard/
├── app.py                  # Streamlit dashboard (main app)
├── data/
│   └── nassau_candy_cleaned.csv   # Cleaned dataset used by the dashboard
├── docs/
│   ├── Nassau_Candy_Research_Paper.docx       # Full EDA + findings + recommendations
│   └── Nassau_Candy_Executive_Summary.docx    # 1-page non-technical summary
├── notebooks/
│   └── EDA_analysis.ipynb  # Google Colab notebook — data cleaning, KPI calculation, charts
├── requirements.txt
└── README.md
```

## 🔑 Key Findings

- **Profit is highly concentrated**: 5 of 15 products (33%) generate **95.1%** of total profit — almost all from the Chocolate division.
- **Chocolate division** drives the business: 92.9% of revenue, 95.1% of profit, 67.5% average margin.
- **"Other" division** shows a structural margin problem: 6.8% of revenue but only 4.6% of profit (37.7% avg margin, the lowest of the three divisions).
- **Kazookles** is the clearest risk product: moderate sales (~$1,206) but only **7.7% margin** — a repricing/cost-renegotiation candidate.
- **Factory-level view**: The Other Factory (which makes Kazookles) has an **11.9% margin**, far below the 65–69% at the two Chocolate factories.
- **Margin volatility is near zero** for every product — margins are structurally stable month-to-month, so fixes are one-time, not ongoing.

Full methodology and charts are in [`docs/Nassau_Candy_Research_Paper.docx`](docs/Nassau_Candy_Research_Paper.docx).

## 📊 Dashboard

The Streamlit dashboard has 5 modules:
1. **Product Profitability** — profit leaderboard, margin volatility
2. **Division Performance** — revenue vs. profit by division
3. **Cost vs. Margin Diagnostics** — scatter plot with risk flags
4. **Pareto Analysis** — profit & revenue concentration curves
5. **Factory Performance** — margin by manufacturing factory

With sidebar filters: date range, division, margin threshold, product search.

### Run locally

```bash
git clone <this-repo-url>
cd nassau-candy-dashboard
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Live deployed version:** _[add your Streamlit Cloud link here]_

## 🧪 Methodology

1. **Data Cleaning** — validated 10,194 order records (no missing values, no duplicates, no negative values); fixed one product-name inconsistency; converted date fields.
2. **KPI Calculation** — Gross Margin %, Profit per Unit, Revenue/Profit Contribution %, Margin Volatility.
3. **Product & Division Analysis** — ranking, Star/Niche/Weak/Risk categorization.
4. **Pareto Analysis** — profit and revenue concentration.
5. **Cost Structure Diagnostics** — cost vs. margin scatter, factory-level rollup.

See [`notebooks/EDA_analysis.ipynb`](notebooks/EDA_analysis.ipynb) for the full step-by-step analysis.

## 🛠️ Tech Stack

- **Python** (pandas, matplotlib) — data cleaning & EDA (Google Colab)
- **Streamlit + Plotly** — interactive dashboard
- **Word/docx** — research paper & executive summary

## 👤 Author

**Kalyani** — B.Tech CSE, Rajiv Gandhi University of Knowledge Technologies
Project submitted as part of the Machine Learning Internship at Unified Mentor Pvt. Ltd.