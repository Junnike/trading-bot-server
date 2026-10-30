#!/bin/bash
# Copies the small, valuable derived files (results, tables, aggregates) into backup/ so they can be pushed to GitHub.
# Raw data (data/poly 14G, data/prints, data/binance, ...) is NOT copied: re-pullable by src/d*.py and src/t*_pull*.py.
cd "$(dirname "$0")/.." || exit 1
B=backup; mkdir -p $B/data
cd data
for f in *.md *.txt *.csv prints_win.parquet prints_cells.parquet prints_agg.parquet poly_resolution.parquet t8c_crowd.parquet t4_poll.jsonl series.json; do [ -e "$f" ] && cp -r --parents "$f" ../$B/data/; done
for f in candle_parts t8b/*.txt t8b/cfg.json t9/*.csv t11_kalshi/cells*.csv t11_kalshi/analysis.txt t11_poly/cells_all.csv t11_poly/summary.json t11_poly/table.md scalpers/metrics.json scalpers/ranking.json scalpers/candidates.json tradfi leadlag/*.csv leadlag/*.json leadlag/*.log t13/analysis.txt t13/replay.parquet; do [ -e "$f" ] || [ -n "$(ls $f 2>/dev/null)" ] && cp -r --parents $f ../$B/data/ 2>/dev/null; done
# 1-second log: keep only key assets, 1s resolution, parquet (full log is too big for git)
cd ..
python3 -I - <<'PY'
import glob, gzip, json, os
try:
    import pandas as pd
except ImportError:
    raise SystemExit("pandas missing: skip seclog")
keys = ("BTC","ETH","SOL","xyz:TSLA","xyz:GOLD","xyz:SILVER","xyz:BRENTOIL","xyz:CL","xyz:NVDA","xyz:SP500","xyz:XYZ100")
rows = []
for fn in sorted(glob.glob("data/seclog/mids_*.jsonl.gz")):
    try:
        with gzip.open(fn, "rt") as f:
            for line in f:
                try: d = json.loads(line)
                except Exception: break
                r = {"t": d["t"]}; r.update({k: v for k, v in d["p"].items() if k in keys}); rows.append(r)
    except Exception: pass
if rows:
    os.makedirs("backup/data/seclog", exist_ok=True)
    pd.DataFrame(rows).to_parquet("backup/data/seclog/keyassets_1s.parquet")
    print("seclog rows", len(rows))
PY
du -sh backup
