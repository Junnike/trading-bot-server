#!/usr/bin/env python3 -I
"""T14 end-of-week report from the okx_logger CSVs. Writes results/T14_live_result.md.
Usage: python3 -I src/okx_report.py [log_dir] [notional_usdt=1000]
Backtest assumptions compared against: OKX basic borrow APR, fees 2 bp per leg-side, zero slippage, basis drift -3 %/yr."""
import os, sys, csv, math
LOGDIR = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/okx_log")
NOTIONAL = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def rd(name):
    p = os.path.join(LOGDIR, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def fl(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


snaps, ints, fills, fails = rd("snapshots.csv"), rd("intervals.csv"), rd("fills.csv"), rd("orders_failed.csv")
if not snaps:
    print("no snapshots.csv in", LOGDIR); sys.exit(1)
t0, t1 = snaps[0]["ts"], snaps[-1]["ts"]
import datetime as dt
def pts(s): return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
days = max((pts(t1) - pts(t0)).total_seconds() / 86400, 1e-9)
ann = lambda usdt: usdt / NOTIONAL / days * 365 * 100   # % per year on one-leg notional

funding = sum(fl(r["funding_received_usdt"], 0) for r in ints)
interest = sum(fl(r["interest_usdt"], 0) for r in ints)
fees = 0.0; slip = 0.0; n_fills = 0
for x in fills:
    px, sz, fee = fl(x["px"]), fl(x["sz"]), fl(x["fee"], 0)
    fees += abs(fee if x["feeCcy"] == "USDT" else fee * px)
    mid = fl(x["mid_at_log"])
    if mid == mid and px == px:
        # buyer pays above mid, seller receives below mid -> both are costs when positive
        slip += ((px - mid) if x["side"] == "buy" else (mid - px)) * sz
        n_fills += 1
# basis PnL: long perp / short spot => gain when perp rises relative to spot
open_snaps = [r for r in snaps if fl(r.get("perp_pos"), 0) != 0 and fl(r.get("perp_last")) == fl(r.get("perp_last"))]
basis_pnl = 0.0
if len(open_snaps) >= 2:
    b0 = fl(open_snaps[0]["basis_pct"]) / 100; b1 = fl(open_snaps[-1]["basis_pct"]) / 100
    basis_pnl = (b1 - b0) * NOTIONAL
net = funding - interest - fees - slip + basis_pnl
coins = []
for r in snaps:
    if not coins or coins[-1] != r["coin"]:
        coins.append(r["coin"])
switches = len(coins) - 1
err_runs = sum(1 for r in snaps if r.get("err"))
borrow_aprs = [fl(r["borrow_apr_pct"]) for r in open_snaps if fl(r["borrow_apr_pct"]) == fl(r["borrow_apr_pct"])]
fund_anns = [fl(r["funding_ann_to_long_pct"]) for r in open_snaps if fl(r["funding_ann_to_long_pct"]) == fl(r["funding_ann_to_long_pct"])]
avail_fail = sum(1 for x in fails if x["instId"].endswith("-USDT") and x["side"] == "sell")

L = [f"# T14 live result — OKX reverse carry, {t0[:10]} .. {t1[:10]} ({days:.1f} days), coins {' -> '.join(coins)}, notional {NOTIONAL:.0f} USDT per leg\n",
     "| line | USDT over the test | %/yr on one-leg notional | backtest assumption | delta |\n|---|---|---|---|---|",
     f"| funding received | {funding:+.2f} | {ann(funding):+.1f} | screen value at entry ({(sum(fund_anns)/len(fund_anns)) if fund_anns else float('nan'):+.0f} avg while open) | {ann(funding) - (sum(fund_anns)/len(fund_anns) if fund_anns else float('nan')):+.1f} |",
     f"| borrow interest | {-interest:+.2f} | {-ann(interest):+.1f} | OKX basic APR ({(sum(borrow_aprs)/len(borrow_aprs)) if borrow_aprs else float('nan'):.0f} avg while open) | {-ann(interest) + (sum(borrow_aprs)/len(borrow_aprs) if borrow_aprs else float('nan')):+.1f} |",
     f"| fees ({len(fills)} fills) | {-fees:+.2f} | {-ann(fees):+.1f} | 2 bp per leg-side | {-ann(fees) - (-(len(fills)) * 0.0002 * NOTIONAL / NOTIONAL / days * 365 * 100):+.1f} |",
     f"| slippage vs mid ({n_fills} fills) | {-slip:+.2f} | {-ann(slip):+.1f} | 0 | {-ann(slip):+.1f} |",
     f"| basis drift (perp vs spot while open) | {basis_pnl:+.2f} | {ann(basis_pnl):+.1f} | −3 %/yr | {ann(basis_pnl) + 3:+.1f} |",
     f"| **net** | **{net:+.2f}** | **{ann(net):+.1f}** | +15 %/yr (OKX-only backtest) | {ann(net) - 15:+.1f} |",
     f"\nFill failures: {len(fails)} (spot-sell = borrow-side: {avail_fail}); coin switches: {switches}; runs with API errors: {err_runs} of {len(snaps)}; funding intervals logged: {len(ints)}."]
verdict = "PASS" if (ann(net) > 10 and avail_fail == 0) else ("FAIL (availability)" if avail_fail > 0 else "FAIL (cost)")
L.append(f"\n**Verdict: {verdict}** (rule: net > +10 %/yr AND no borrow-side fill failure).")
os.makedirs(RES, exist_ok=True)
open(os.path.join(RES, "T14_live_result.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
