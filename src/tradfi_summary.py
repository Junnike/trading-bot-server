"""Per-venue summary (counts by category, notable names, fee/leverage modes, hours) -> data/tradfi/summary_by_venue.json"""
import json, pathlib, collections
import pandas as pd
D = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
df = pd.read_parquet(D / "markets_all.parquet")
h = json.load(open(D / "history_binance_bybit.json"))
rows = []
for v in ("binance", "bybit"):
    for s, x in h[v].items():
        if s == "USDEUSDT": continue
        rows.append(dict(venue={"binance": "Binance", "bybit": "Bybit"}[v], symbol=s, base=x["base"], cat=x["cat"], maker=None, taker=None, max_lev=None, hours="24/7", status="TRADING", tag="dump", listed_first=x["first"]))
df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
df.to_parquet(D / "markets_all_with_binance_bybit.parquet")
df.to_json(D / "markets_all_with_binance_bybit.json", orient="records")
PRI = "TSLA NVDA AAPL MSFT AMZN GOOGL META MSTR COIN HOOD PLTR AMD INTC MU CRCL XAU GOLD XAG SILVER XPT XPD COPPER CL WTI BRENT BRENTOIL NATGAS SP500 SPX500 US500 NAS100 NDX US100 US30 DJI JP225 HSI KR200 EUR EURUSD GBPUSD USDJPY QQQ SPY IWM EWY SOXL OPENAI ANTHROPIC SPCX SPACEX UNITREE SAMSUNG SKHYNIX".split()
out = {}
for v, g in df.groupby("venue"):
    c = g.cat.value_counts().to_dict()
    names = [b for b in PRI if b in set(g.base)]
    rest = [b for b in g.base.unique() if b not in names]
    cnt = {k: int(c.get(k, 0)) for k in ("stocks", "indices", "commodities", "fx", "etf", "preipo", "other")}
    ent = dict(total=int(len(g)), unique_underlyings=int(g.base.nunique()), **cnt, names=(names + rest)[:15])
    for col in ("maker", "taker", "max_lev"):
        x = g[col].dropna()
        if len(x): ent[col] = dict(min=float(x.min()), max=float(x.max()), mode=float(x.mode().iloc[0]))
    ent["hours"] = g.hours.dropna().value_counts().to_dict()
    out[v] = ent
json.dump(out, open(D / "summary_by_venue.json", "w"), indent=1, ensure_ascii=False)
for v, e in sorted(out.items(), key=lambda kv: -kv[1]["total"]): print(v, {k: e[k] for k in e if k != "names"}, "\n   ", e["names"])
