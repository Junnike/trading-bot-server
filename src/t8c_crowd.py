# T8c step 1: per-window crowding proxy = taker contracts traded at price<=0.45 (either token), age 0..300 s. -> data/t8c_crowd.parquet
import glob, os, pandas as pd
D = "data"; rows = []
for f in sorted(glob.glob(f"{D}/poly/*_trades.parquet")):
    d = os.path.basename(f)[:10]
    mk = pd.read_parquet(f"{D}/poly/{d}_markets.parquet", columns=["cid", "start"])
    tr = pd.read_parquet(f, columns=["cid", "price", "size", "ts"])
    tr = tr.merge(mk, on="cid"); tr["age"] = tr.ts - tr.start
    tr = tr[(tr.age >= 0) & (tr.age <= 300)]
    g = pd.DataFrame({"start": tr.start, "lo": tr["size"].where(tr.price <= 0.45, 0.0), "all": tr["size"]}).groupby("start").sum()
    rows.append(g)
pd.concat(rows).reset_index().to_parquet(f"{D}/t8c_crowd.parquet")
