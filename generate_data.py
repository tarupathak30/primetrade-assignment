"""
Synthetic data generator for Primetrade.ai assignment.
Produces datasets that structurally mirror the described Hyperliquid + Fear/Greed data.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

# ── 1. Fear/Greed Sentiment ──────────────────────────────────────────────────
dates = pd.date_range("2023-01-01", "2024-06-30", freq="D")
n_days = len(dates)

# Regime transitions: clusters of fear/greed
raw = np.cumsum(np.random.randn(n_days) * 0.4)
raw = (raw - raw.min()) / (raw.max() - raw.min()) * 100
classification = pd.cut(raw, bins=[0, 40, 60, 100],
                        labels=["Fear", "Neutral", "Greed"])
# Simplify to binary as assignment describes
classification = classification.map({"Fear": "Fear", "Neutral": "Fear", "Greed": "Greed"})

sentiment_df = pd.DataFrame({"date": dates, "score": raw.round(1),
                              "classification": classification})
sentiment_df.to_csv("/home/claude/primetrade_project/data/sentiment.csv", index=False)
print(f"Sentiment rows: {len(sentiment_df)}, Fear: {(sentiment_df.classification=='Fear').sum()}, Greed: {(sentiment_df.classification=='Greed').sum()}")

# ── 2. Hyperliquid Trader Data ───────────────────────────────────────────────
accounts = [f"0x{i:04x}" for i in range(1, 201)]   # 200 traders
symbols   = ["BTC", "ETH", "SOL", "ARB", "AVAX"]

# Trader archetypes
archetype = {}
for acc in accounts:
    r = np.random.rand()
    if   r < 0.15: archetype[acc] = "whale"         # large size, moderate freq
    elif r < 0.35: archetype[acc] = "high_leverage"  # high lev, mixed PnL
    elif r < 0.60: archetype[acc] = "scalper"        # high freq, small size
    elif r < 0.80: archetype[acc] = "swing"          # low freq, larger size
    else:          archetype[acc] = "passive"         # low freq, low leverage

rows = []
trade_id = 1
for date in dates:
    sent = sentiment_df.loc[sentiment_df.date == date, "classification"].values[0]
    sent_fear = (sent == "Fear")

    for acc in accounts:
        arch = archetype[acc]

        # Base trades per day by archetype
        base_trades = {"whale": 3, "high_leverage": 5, "scalper": 12,
                       "swing": 1, "passive": 0.4}[arch]
        # Sentiment effect on frequency
        freq_mult = 0.7 if sent_fear else 1.2
        n_trades = max(0, int(np.random.poisson(base_trades * freq_mult)))

        for _ in range(n_trades):
            symbol = np.random.choice(symbols, p=[0.5, 0.25, 0.1, 0.08, 0.07])
            side   = "long" if np.random.rand() > (0.55 if sent_fear else 0.42) else "short"

            # Leverage by archetype + sentiment
            lev_base = {"whale": 5, "high_leverage": 18, "scalper": 8,
                        "swing": 4, "passive": 3}[arch]
            lev_adj  = lev_base * (0.85 if sent_fear else 1.1)
            leverage = max(1, int(np.random.lognormal(np.log(lev_adj), 0.3)))

            size_base = {"whale": 50000, "high_leverage": 8000, "scalper": 2000,
                         "swing": 20000, "passive": 5000}[arch]
            size = max(100, np.random.lognormal(np.log(size_base), 0.5))

            exec_price = np.random.uniform(20000, 70000) if symbol == "BTC" else \
                         np.random.uniform(1000, 4000)   if symbol == "ETH" else \
                         np.random.uniform(10, 200)

            # PnL: fear days slightly worse; high leverage more volatile
            pnl_sigma = 0.02 * leverage * size / 1000
            pnl_mu    = -0.001 if sent_fear else 0.002
            if arch == "high_leverage": pnl_mu -= 0.002
            closed_pnl = np.random.normal(pnl_mu * size, pnl_sigma)

            rows.append({
                "account":        acc,
                "symbol":         symbol,
                "execution_price": round(exec_price, 2),
                "size":           round(size, 2),
                "side":           side,
                "time":           pd.Timestamp(date) + pd.Timedelta(seconds=np.random.randint(0, 86400)),
                "start_position": round(np.random.uniform(-size, size), 2),
                "event":          np.random.choice(["TRADE", "LIQUIDATION"], p=[0.96, 0.04]),
                "closedPnL":      round(closed_pnl, 4),
                "leverage":       leverage,
                "archetype":      arch,
            })
            trade_id += 1

trades_df = pd.DataFrame(rows)
trades_df.to_csv("/home/claude/primetrade_project/data/trades.csv", index=False)
print(f"Trades rows: {len(trades_df)}, columns: {list(trades_df.columns)}")
print(trades_df.head(3))
