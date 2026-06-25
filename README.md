# PROC Rebate Hunter

**An agentic AI prototype that finds volume rebates a corporation is contractually owed but never claims — because the same supplier is fragmented across dozens of SAP vendor accounts.**

🔗 **Live demo:** https://prockickbackhunter.streamlit.app/
🖥️ **Stack:** Python · Streamlit · pandas · plotly (single file, ~800 lines)
🗣️ **Demo UI language:** German, deliberately written in plain language (KISS) so anyone — without procurement or AI background — can follow it.

> ℹ️ The repository and deployment slug still read *"kickback"* — that name predates a deliberate terminology fix. *Kickback* means a bribe in English; the correct term for a contractual volume bonus is a **rebate** (German: *Rückvergütung*). The application has been fully renamed to **PROC Rebate Hunter**.

---

## The business problem (in one paragraph)

A large corporation buys from a supplier under a rebate agreement: spend more than a threshold per year (here **€50.0 m**) and you get **2 %** back. But over years of mergers and across multiple booking areas and countries, that one supplier ends up stored in SAP as **many separate vendor accounts** under slightly different names. Standard ERP reporting checks **each account on its own**, sees that every single one is below the threshold, and reports **"no claim."** In reality the accounts belong to the same economic entity, and the combined spend is over the line. The money quietly stays on the table.

### The showcase number

| Entity | SAP accounts | Largest single account | Consolidated spend | Threshold | Result |
|---|---|---|---|---|---|
| **Cisco** (incl. Meraki, Acacia, Splunk) | 5 | €18.20 m | **€52.40 m** | €50.0 m | ✅ **Rebate: €1,048,000** |
| **Microsoft** (incl. Activision Blizzard) | 2 | €41.00 m | €47.00 m | €50.0 m | ❌ Honest negative — below threshold |
| **Apex** look-alike pair | 2 | €2.30 m | — | — | ⚠️ Deliberately **not** merged (different owners) |

No standalone Cisco account reaches €50 m. Only after the fragments are correctly linked does the €1,048,000 claim become visible.

---

## How it works

A single guided screen runs a **process token** (one Python dict) through **six agents**. Each agent reads the token, does its job, enriches the token with its result **and its evidence**, and hands it on. There is **exactly one** human decision point — everything before and after it runs autonomously.

```
📥 Ingestion → 🧩 Resolution → 📄 Contract → 🧮 Finance → 🧑‍⚖️ Human review → ✅ Booking
   (sim)         (live)          (sim)         (live)        (the only gate)     (sim)
```

1. **Ingestion** — pulls all suppliers and invoices into the token.
2. **Resolution** *(the core)* — decides which accounts are really the same company and consolidates them. **Aus 5 Silos wird 1 Entität.**
3. **Contract** — extracts the relevant clause: rebate rate and threshold.
4. **Finance** — sums the consolidated spend, compares it to the threshold, computes the rebate (the € value).
5. **Human-in-the-loop** — a person reviews the evidence and the verdict and **approves or rejects once, with a mandatory reason code.**
6. **Booking** — only on approval: parks the accounting document and drafts (never sends) a notification to the CFO.

The token visibly grows stage by stage (shown as JSON in an expander), a header pipeline bar highlights the current stage (`pending → active → done`), and every agent action is written to an **append-only audit log** (CSV export included). Stage transitions use a short, **clearly labelled simulated model-latency** so the flow reads like a real GenAI agent at work — no hidden logic is faked.

---

## Why it can be trusted

This prototype was built to be **auditable and honest**, not to look magical.

### Entity resolution with discipline
- **The only authority for merging accounts is a verified shared corporate parent** (a simulated GLEIF/D&B company register).
- **Similar names and the same city are explicitly *not* merge signals.** That is the difference between a real M&A link and a dangerous false match.
- The **Apex** pair (`Apex Robotics Solutions GmbH` vs `Apex Robotics Systems Ltd.`) has **66.7 %** name similarity but two different owners → the app **refuses to merge them** and flags them for review.
- Conversely, **Cisco ↔ Meraki** share only **23.1 %** name similarity yet are the same group → a naive name matcher would *miss* this real link; only the verified register catches it.
- Both figures are computed live with Python's `difflib` so you can see *why* names alone are not enough.

### Measured quality (EU AI Act / audit evidence)
Resolution accuracy is measured pairwise against labelled ground truth, in real time:

| Metric | Value |
|---|---|
| Precision (no wrong merges) | **100 %** |
| Recall (nothing missed) | **100 %** |
| False merges | **0** |

These numbers are **computed, not hard-coded.**

---

## Honesty by design — LIVE vs SIMULATED

Every stage is labelled. What is real logic is marked **LIVE**; what is stubbed for the demo is marked **SIMULATED** (no fake enterprise integrations are claimed).

| Capability | Status |
|---|---|
| Deterministic, explainable entity resolution | 🟢 **LIVE** |
| Confidence & evidence per cluster | 🟢 **LIVE** |
| Accuracy measurement (precision / recall / false merges) | 🟢 **LIVE** |
| Spend consolidation & threshold check | 🟢 **LIVE** |
| Human-in-the-loop approval with reason code | 🟢 **LIVE** |
| Append-only audit log + CSV export | 🟢 **LIVE** |
| SAP read / posting (RFC, BAPI) | 🟠 SIMULATED |
| Corporate-parent register (GLEIF / D&B) | 🟠 SIMULATED |
| Contract-clause extraction (LLM / RAG) | 🟠 SIMULATED |
| CFO e-mail | 🟠 SIMULATED — **draft only, never sent** |
| GenAI processing time between stages | 🟠 SIMULATED — labelled as such |

---

## Run it locally

```bash
git clone https://github.com/VictorPflueger/PROC-Kickback-Hunter.git
cd PROC-Kickback-Hunter

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (default http://localhost:8501).

### Deploy on Streamlit Community Cloud
Point a new app at this repository with `app.py` as the entrypoint — no secrets or external services are required, because all data is generated in memory.

---

## Project structure

```
.
├── app.py            # the entire application (single file)
├── requirements.txt  # streamlit, pandas, plotly
└── README.md
```

## Tech stack

- **Streamlit** for the single-screen UI and session state
- **pandas** for the in-memory SAP-style tables (LFA1 vendors, EKKO purchase orders)
- **plotly** for the consolidated-vs-threshold chart
- **Python standard library only** for the logic: `difflib` (name similarity), plus `json`, `time`, `random`, `datetime`

No database, no API keys, no external calls — everything runs from `requirements.txt`.

---

## Data & scenario notes

- All **150 suppliers** are generated **in memory** from a fixed random seed, so the demo is fully deterministic and reproducible.
- 9 named "core" vendors carry the storyline (Cisco group, Microsoft cluster, the Apex look-alike pair); 141 generic vendors provide realistic noise.
- The figures (€52.40 m → €1,048,000; €47.00 m below threshold) are exact and stable across runs.

## Limitations

This is a **demonstration prototype**, not a production system. It uses synthetic data and is **not connected to any real SAP system**. The stubbed parts (SAP I/O, company register, clause extraction, SSO) mark exactly where real enterprise integrations would go. Nothing is posted or e-mailed for real.

---

## Author

**Victor Pflüger** — Senior Consultant, Data Science & AI · [linkedin.com/in/victorpflueger](https://www.linkedin.com/in/victorpflueger)

*Built as a portfolio prototype to show how an agentic, human-supervised workflow can surface real, auditable value in enterprise procurement.*
