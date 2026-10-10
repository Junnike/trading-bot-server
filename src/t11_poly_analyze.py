# Stage 4: calibration cells. Reads data/t11_poly/sample.jsonl + entries.jsonl -> cells_all.csv, summary.json
import json, sys, math, collections, datetime as dt
import numpy as np, pandas as pd
D = 'data/t11_poly/'
FEE = 0.07; HOLD = ('2026-08', '2026-09')
S = {}
for l in open(D + 'sample.jsonl'):
    m = json.loads(l); S[m['cid']] = m
rows = []; drop = collections.Counter()
for l in open(D + 'entries.jsonl'):
    e = json.loads(l); m = S[e['cid']]; life = m['close'] - m['start']
    for f, h in e['res'].items():
        if h is None: drop['api_error'] += 1; continue
        if not h: drop['no_trade_point_in_window'] += 1; continue
        t, p = h[0]; T = m['start'] + float(f) * life
        if t - T > 0.1 * life + 600: drop['lag_too_big'] += 1; continue
        if t >= m['close']: drop['at_or_after_close'] += 1; continue
        for side, price, win in ((0, p, m['yes']), (1, 1 - p, 1 - m['yes'])):
            if not (0.01 <= price <= 0.99): drop['price_outside_1_99'] += 1; continue
            d = dt.datetime.fromtimestamp(m['close'], dt.timezone.utc)
            rows.append((m['cat'], float(f), side, price, win, d.strftime('%Y-%m-%d'), d.strftime('%Y-%m'), m['vol'], m['cid']))
df = pd.DataFrame(rows, columns=['cat', 'tf', 'side', 'p', 'win', 'day', 'month', 'vol', 'cid'])
df['fee'] = FEE * df.p * (1 - df.p); df['ev'] = (df.win - df.p - df.fee) * 100
edges = [0, .05, .10, .20, .30, .50, .70, .90, .95, 1.0001]; labs = ['0-5', '5-10', '10-20', '20-30', '30-50', '50-70', '70-90', '90-95', '95-100']
df['bucket'] = pd.cut(df.p, edges, labels=labs, right=False)
df.to_parquet(D + 'obs.parquet')
rng = np.random.default_rng(5)
def boot(g):
    c = g.groupby('day').ev.agg(['sum', 'count']); s = c['sum'].values; n = c['count'].values
    idx = rng.integers(0, len(s), (2000, len(s)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return m.mean() / m.std() if m.std() > 0 else float('nan')
out = []
for (cat, tf, b), g in df[~df.month.isin(HOLD)].groupby(['cat', 'tf', 'bucket'], observed=True):
    if len(g) < 30: continue
    mm = g.groupby('month').ev.agg(['mean', 'count']); mm = mm[mm['count'] >= 10]
    h = df[(df.cat == cat) & (df.tf == tf) & (df.bucket == b) & df.month.isin(HOLD)]
    out.append(dict(cat=cat, tf=tf, bucket=b, n=len(g), mkts=g.cid.nunique(), win=g.win.mean(), price=g.p.mean(), ev=g.ev.mean(), z=boot(g),
                    months_pos=int((mm['mean'] > 0).sum()), months=len(mm), hold_n=len(h), hold_ev=h.ev.mean() if len(h) else float('nan')))
R = pd.DataFrame(out); N = len(R)
from statistics import NormalDist
NF = 8 * 3 * 9; zthr = NormalDist().inv_cdf(1 - 0.05 / (2 * NF))
R['alive'] = (R.n >= 200) & (R.z >= zthr) & (R.months_pos >= 0.6 * R.months) & (R.hold_ev > 0) & (R.ev >= 1)
R.to_csv(D + 'cells_all.csv', index=False)
summ = dict(obs=len(df), markets=df.cid.nunique(), cells_tested=N, bonf_z=zthr, alive=int(R.alive.sum()), drop=dict(drop),
            obs_by_cat=df.groupby('cat').cid.nunique().to_dict(), months=sorted(df.month.unique())[:1] + sorted(df.month.unique())[-1:], holdout_obs=int(df.month.isin(HOLD).sum()),
            cells_n200=int((R.n >= 200).sum()), cells_z2=int(((R.n >= 200) & (R.z >= 2)).sum()), cells_ev1=int(((R.n >= 200) & (R.ev >= 1)).sum()))
json.dump(summ, open(D + 'summary.json', 'w'), indent=1, default=str); print(json.dumps(summ, default=str))
pd.set_option('display.width', 250)
print(R[R.n >= 200].sort_values('z', ascending=False).head(20).round(3).to_string())
print(R[R.n >= 200].sort_values('z').head(5).round(3).to_string())
