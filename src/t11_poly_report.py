import json, numpy as np, pandas as pd
D = 'data/t11_poly/'; HOLD = ('2026-08', '2026-09')
R = pd.read_csv(D + 'cells_all.csv'); df = pd.read_parquet(D + 'obs.parquet'); S = json.load(open(D + 'summary.json')); C = json.load(open(D + 'select_counts.json'))
rng = np.random.default_rng(7)
def boot(g):
    c = g.groupby('day').ev.agg(['sum', 'count']); s = c['sum'].values; n = c['count'].values
    idx = rng.integers(0, len(s), (2000, len(s))); m = s[idx].sum(1) / n[idx].sum(1); return m.mean() / m.std()
pool = []
for b, g in df[~df.month.isin(HOLD)].groupby('bucket', observed=True):
    h = df[(df.bucket == b) & df.month.isin(HOLD)]; mm = g.groupby('month').ev.agg(['mean', 'count']); mm = mm[mm['count'] >= 10]
    pool.append(dict(cat='ALL', tf='all', bucket=b, n=len(g), win=g.win.mean(), price=g.p.mean(), ev=g.ev.mean(), z=boot(g), mp=f"{(mm['mean']>0).sum()}/{len(mm)}", hold=h.ev.mean()))
P = pd.DataFrame(pool)
T = R[R.n >= 200].sort_values('z', ascending=False).head(7).copy(); T['mp'] = T.months_pos.astype(str) + '/' + T.months.astype(str); T = T.rename(columns={'hold_ev': 'hold'})
lines = ['| category | venue | tf | bucket | n obs | win | price | EV c/ct | z | months+ | holdout EV |', '|---|---|---|---|---|---|---|---|---|---|---|']
f = lambda r: f"| {r.cat} | Poly | {r.tf} | {r.bucket} | {r.n} | {r.win:.3f} | {r.price:.3f} | {r.ev:+.2f} | {r.z:+.2f} | {r.mp} | {r.hold:+.2f} |"
for r in T.itertuples(): lines.append(f(r))
for r in P.itertuples(): lines.append(f(r))
open(D + 'table.md', 'w').write('\n'.join(lines)); print('\n'.join(lines))
byc = df[~df.month.isin(HOLD)].groupby('cat').agg(n=('ev', 'size'), ev=('ev', 'mean')); print(byc.round(2))
print(df.groupby('cat').cid.nunique(), df.month.min(), df.month.max(), df.groupby('month').cid.nunique().describe())
print(df.groupby('tf').size())
