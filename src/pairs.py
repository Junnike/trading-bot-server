"""T13 statistical pairs trading on Binance USDT perps (hourly). Run: python3 -I src/pairs.py"""
import numpy as np, pandas as pd, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEL_H, STEP, ZW = 2160, 720, 168
TAKER, MAKER, NPAIRS_CAP = 20.0, 8.0, 20
rng = np.random.default_rng(0)

px = pd.read_pickle(f'{ROOT}/data/cache/panel_perp.pkl')
qv = pd.read_pickle(f'{ROOT}/data/cache/panel_qv.pkl')
idx = px.index
LP_all = np.log(px.values.astype(float))
P_all = px.values.astype(float)

def universe(n):
    recent = px.loc['2024-01-01':'2026-09-30']
    ok = recent.isna().mean() <= 0.05
    m = qv.mean().where(ok).dropna().sort_values(ascending=False)
    return list(m.index[:n])

def select(cols, r0, k=NPAIRS_CAP):
    """Pairs chosen with bars [r0-SEL_H, r0-1]. Greedy, disjoint (no shared symbol)."""
    L = LP_all[r0 - SEL_H:r0][:, cols]
    n = L.shape[1]
    valid = ~np.isnan(L).any(0)
    L = np.where(valid, L, 0.0)
    ret = np.diff(L, axis=0)
    C = np.corrcoef(ret.T)
    Lc = L - L.mean(0)
    var = (Lc ** 2).mean(0)
    cands = []
    for i in range(n):
        if not valid[i]: continue
        js = np.arange(i + 1, n)
        js = js[valid[js]]
        if len(js) == 0: continue
        beta = (Lc[:, [i]] * Lc[:, js]).mean(0) / var[js]
        S = L[:, [i]] - beta * L[:, js]
        x, d = S[:-1], np.diff(S, axis=0)
        xc, dc = x - x.mean(0), d - d.mean(0)
        phi = (xc * dc).sum(0) / (xc ** 2).sum(0)
        with np.errstate(all='ignore'):
            hl = -np.log(2) / np.log(1 + phi)
        good = (phi < 0) & (phi > -1) & (hl > 0) & (hl <= 72) & (C[i, js] >= 0.5)
        for jj in np.where(good)[0]:
            cands.append((hl[jj], i, js[jj], beta[jj]))
    cands.sort()
    used, out = set(), []
    for hl, i, j, b in cands:
        if i in used or j in used: continue
        used |= {i, j}; out.append((cols[i], cols[j], b, hl))
        if len(out) >= k: break
    return out

def rolling_z(S, start, end):
    """z for bars start..end-1 using only spread through t-1 (168h window)."""
    s = pd.Series(S)
    m = s.rolling(ZW).mean().shift(1); sd = s.rolling(ZW).std().shift(1)
    return ((s.shift(1) - m) / sd).values[start:end]

def run(n_univ=50, entry=2.0, exit_z=0.5, stop=4.0, maxhold=72, sel_cache={}):
    names = universe(n_univ)
    cols = [px.columns.get_loc(c) for c in names]
    trades = []
    rebs = list(range(SEL_H, len(idx) - 1, STEP))
    for r0 in rebs:
        key = (n_univ, r0)
        if key not in sel_cache: sel_cache[key] = select(cols, r0)
        r1 = min(r0 + STEP, len(idx) - 1)   # rebalance bar index: forced exit at its close
        for a, b, beta, hl in sel_cache[key]:
            ia, ib = a, b
            lo = r0 - ZW - 2
            S = LP_all[lo:r1 + 1, ia] - beta * LP_all[lo:r1 + 1, ib]
            z = rolling_z(S, r0 - lo, r1 + 1 - lo)  # z[k] for bar r0+k
            pa, pb = P_all[r0:r1 + 1, ia], P_all[r0:r1 + 1, ib]
            T = len(z); k = 0
            while k < T:
                if k < T - 1 and not np.isnan(z[k]) and abs(z[k]) >= entry and not (np.isnan(pa[k]) or np.isnan(pb[k])):
                    sgn = -np.sign(z[k]); e = k; j = k + 1
                    while True:
                        zz = z[j]
                        if j == T - 1 or j - e >= maxhold or (not np.isnan(zz) and (abs(zz) <= exit_z or abs(zz) >= stop)):
                            break
                        j += 1
                    if not (np.isnan(pa[j]) or np.isnan(pb[j])):
                        g = 1e4 * sgn * ((pa[j] / pa[e] - 1) - (pb[j] / pb[e] - 1))
                        trades.append((idx[r0 + e], j - e, g))
                    k = j + 1
                else:
                    k += 1
    df = pd.DataFrame(trades, columns=['t', 'hold', 'gross'])
    return df, rebs

def boot_z(df, B=2000):
    if len(df) < 2: return np.nan
    day = df['t'].dt.floor('D')
    g = df.groupby(day)['gross'].agg(['sum', 'count'])
    s, c = g['sum'].values, g['count'].values
    ii = rng.integers(0, len(s), (B, len(s)))
    means = s[ii].sum(1) / c[ii].sum(1)
    return means.mean() / means.std(ddof=1) if means.std() > 0 else np.nan

def stats(df, days):
    if len(df) == 0: return dict(n=0)
    return dict(n=len(df), win=(df.gross > 0).mean(), gross=df.gross.mean(), taker=df.gross.mean() - TAKER,
                maker=df.gross.mean() - MAKER, z=boot_z(df), hold=df.hold.median(), tpd=len(df) / days,
                ann=(df.gross - MAKER).sum() / 1e4 / NPAIRS_CAP * 365 / days)

def table(df, t0, t1, first_day, label_years):
    rows = []
    for y in label_years + ['ALL']:
        if y == 'ALL': a, b = pd.Timestamp(max(t0, first_day)), t1
        else:
            a = max(pd.Timestamp(f'{y}-01-01', tz='UTC'), first_day, t0); b = min(pd.Timestamp(f'{y}-12-31 23:59', tz='UTC'), t1)
        sub = df[(df.t >= a) & (df.t <= b)]
        days = max((b - a).total_seconds() / 86400, 1)
        s = stats(sub, days); s['y'] = y; rows.append(s)
    hdr = '| Period | Trades | Win% (gross>0) | Gross bp | Net bp taker (20) | Net bp maker (8) | Boot z (gross) | Median hold h | Trades/day | Ann. net maker |\n|---|---|---|---|---|---|---|---|---|---|\n'
    out = ''
    for s in rows:
        if s['n'] == 0: out += f"| {s['y']} | 0 | | | | | | | | |\n"; continue
        out += f"| {s['y']} | {s['n']} | {100*s['win']:.1f}% | {s['gross']:.2f} | {s['taker']:.2f} | {s['maker']:.2f} | {s['z']:.2f} | {s['hold']:.0f} | {s['tpd']:.2f} | {100*s['ann']:.1f}% |\n"
    return hdr + out, rows

if __name__ == '__main__':
    t_start = time.time()
    df, rebs = run()
    print('base done', len(df), f'{time.time()-t_start:.0f}s', flush=True)
    first_day = idx[rebs[0]]; t1 = idx[-1]
    tA, rowsA = table(df, idx[0], t1, first_day, [2022, 2023, 2024, 2025, 2026])
    t25 = pd.Timestamp('2025-01-01', tz='UTC')
    tB, rowsB = table(df[df.t >= t25], t25, t1, first_day, [2025, 2026])
    full, late = rowsA[-1], rowsB[-1]
    variants = [('entry 1.5', dict(entry=1.5)), ('entry 2.5', dict(entry=2.5)), ('max hold 24h', dict(maxhold=24)),
                ('max hold 168h', dict(maxhold=168)), ('universe 30', dict(n_univ=30)), ('universe 100', dict(n_univ=100))]
    sens = '| Variant | Trades | Net bp maker (ALL) | Boot z (gross) |\n|---|---|---|---|\n'
    for name, kw in variants:
        d, _ = run(**kw); s = stats(d, 1)
        sens += f"| {name} | {s.get('n',0)} | {s.get('maker',float('nan')):.2f} | {s.get('z',float('nan')):.2f} |\n"
        print(name, f'{time.time()-t_start:.0f}s', flush=True)
    alive = full['maker'] > 0 and full['z'] >= 2 and late['maker'] > 0 and late['z'] >= 2
    verdict = (f"**Verdict: {'ALIVE' if alive else 'DEAD'}** - full period net maker {full['maker']:.2f} bp/trade, gross z {full['z']:.2f}; "
               f"2025-26 net maker {late['maker']:.2f} bp/trade, gross z {late['z']:.2f} (taker net {full['taker']:.2f} / {late['taker']:.2f}).")
    n_pairs = np.mean([len(select_v) for (nu, _), select_v in run.__defaults__[-1].items() if nu == 50])
    notes = (f"Notes: universe = top-50 by whole-sample mean quote volume after dropping symbols with >5% NaN in 2024-01..2026-09 (selection uses full-sample volume, a mild look-ahead per spec). "
             f"Pairs: 90d trailing (2160 bars before rebalance), rebalance every 30d from {first_day:%Y-%m-%d}; pairs with any NaN in window skipped; chosen greedily by half-life with NO shared symbols (avg {n_pairs:.1f} pairs/period, may be <20; capital still 20 units). "
             f"z uses spread and 168h rolling stats through bar t-1; entry/exit at bar t close; forced exit at rebalance bar close. Sizing 1 unit each leg, beta ignored (only used for spread/signal). "
             f"Trades assigned to period by entry time; win = gross>0; bootstrap clusters by UTC entry day (2000 resamples, z = mean/sd of resampled means). "
             f"Annualised = sum(net maker bp)/1e4/20 scaled by 365/days covered (2022 starts at first rebalance, 2026 ends 09-30). Trades discarded if exit price NaN.")
    md = f"# T13 Pairs trading (hourly Binance USDT perps)\n\n## (a) By year, entry 2, exit 0.5, stop 4, max hold 72h\n\n{tA}\n## (b) 2025-01-01..2026-09-30\n\n{tB}\n## (c) Sensitivity (ALL period)\n\n{sens}\n## (d)\n\n{verdict}\n\n{notes}\n"
    os.makedirs(f'{ROOT}/results', exist_ok=True)
    open(f'{ROOT}/results/T13_pairs.md', 'w').write(md)
    print(f'total {time.time()-t_start:.0f}s')
