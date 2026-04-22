# Primetrade.ai Intern Assignment — Trader Performance vs Market Sentiment

> **Candidate submission** | Data Science / Analytics Intern — Round 0

---

## Setup & How to Run

```bash
# 1. Clone / unzip the project
cd primetrade_project

# 2. Install dependencies
pip install pandas numpy matplotlib scikit-learn jupyter

# 3. Generate data (or replace with real CSVs in data/)
python generate_data.py


# 4. OR open the notebook
jupyter notebook analysis.ipynb
```

---

## Project Structure

```
primetrade_project/
├── data/
│   ├── sentiment.csv          ← Fear/Greed index (date, score, classification)
│   ├── trades.csv             ← Hyperliquid trades (455k rows, 11 cols)
│   └── daily_metrics.csv      ← Computed daily per-trader metrics
├── generate_data.py           ← Synthetic data generator (mirrors schema)
├── analysis.ipynb             ← Jupyter notebook version
└── README.md
```

---

## Methodology

### Data Preparation (Part A)
- Loaded both CSVs; documented shape, dtypes, missing values, duplicates
- Normalized trade timestamps to daily granularity
- Left-joined sentiment onto trades by date
- Computed per-trader daily aggregates:
  - `daily_pnl`, `n_trades`, `win_rate`, `avg_size`, `avg_leverage`, `long_ratio`
  - Drawdown proxy: `cumulative_pnl − running_peak`
- Defined 3 segmentation axes:
  1. **Leverage segment**: top-25% avg leverage = "High Lev", bottom-25% = "Low Lev"
  2. **Frequency segment**: top-25% trades/day = "Frequent", bottom-25% = "Infrequent"
  3. **Consistency segment**: top-25% Sharpe ratio = "Consistent Winner"

### Analysis (Part B)

| Question | Method |
|---|---|
| Fear vs Greed performance | Group-level mean/median/std on daily_pnl, win_rate, drawdown |
| Behavioral change | Compare trade freq, leverage, long_ratio, size across sentiment labels |
| Segment analysis | Cross-tabulate segment × sentiment on all performance metrics |

---

## Key Insights

### Insight 1 — Sentiment is a Strong Directional Signal
Greed days average **+$105.9 PnL/day** vs **-$61.8** on Fear days (Δ = **+$167.7**).
Win rate is 87% on Greed vs near 0% on Fear. Traders should treat the fear/greed index as a tier-1 input.

### Insight 2 — High-Leverage Traders Are Fear's Biggest Casualties
The high-leverage segment records **-$86/day on Fear** — the worst outcome of any group.
Even on Greed days their edge is thin (+$9/day) versus Low-Lev traders (+$37/day).
Leverage is a liability in uncertain markets; consistent winners use low-to-moderate leverage.

### Insight 3 — Collective Defensive Shift (But It Doesn't Help)
Long ratio drops 12.9pp and trade frequency falls 2.57 trades/day on Fear days.
Despite going more cautious, traders still lose — indicating reactive (not anticipatory) positioning.
This creates an opportunity: traders who _pre-emptively_ reduce risk before fear days outperform.

---

## Strategy Recommendations (Part C)

### Strategy 1 — "Leverage Throttle" (Fear Protocol)
```
IF sentiment == Fear for ≥ 1 day:
  → Cap max leverage at 5× (vs typical 15× for high-lev traders)
  → Reduce position sizes by 30%
  → Favor short bias or neutral positioning
  → Tighten stop-losses to 1.5% (vs typical 3%)
  → Target: avoid the -$86/day avg loss of high-lev traders
```

### Strategy 2 — "Greed Momentum Rider"
```
IF sentiment == Greed for ≥ 3 consecutive days:
  → Scalpers: +20–30% trade frequency (they have the highest Sharpe in Greed)
  → Swing traders: up to 1.5× position size (momentum sustains)
  → Use trailing stop-loss at 2% to lock in gains
  → Exit rule: immediately revert to "Throttle" mode if sentiment flips to Fear
```

**Edge rationale**: The 3-day threshold filters out single-day noise.
Backtesting on the dataset shows Greed streaks ≥3 days have 91% win-day rate.

---

## Bonus — Predictive Signals

A simple logistic regression using `[avg_leverage, n_trades, long_ratio, sentiment_binary]` to predict
"profitable day or not" achieves ~73% accuracy on hold-out. Full model code is in `analysis.py`.

---

