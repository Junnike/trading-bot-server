#!/usr/bin/env python3 -I
"""OKX live-test logger (T14 reverse funding carry). Observes only, never trades.

Run every 5 minutes on the droplet (systemd timer in deploy/). Stdlib only.

Env (deploy/okx_logger.env.example):
  OKX_KEY, OKX_SECRET, OKX_PASSPHRASE   read-only API key (IP-whitelist the droplet). Unset -> public-only mode.
  OKX_COIN        e.g. ATOM (the coin currently in the test). Empty -> public-only snapshot of nothing useful.
  OKX_LOG_DIR     default ~/okx_log
  OKX_SIMULATED   "1" for demo trading (adds x-simulated-trading header)

Outputs (append-only CSV in OKX_LOG_DIR):
  snapshots.csv      one row per run: prices, basis, funding, borrow rate/quota, position, equity
  intervals.csv      one row per funding timestamp: funding received, interest, cum sums
  fills.csv          every fill on COIN-USDT and COIN-USDT-SWAP (with mid at log time as slippage proxy)
  orders_failed.csv  cancelled / unfilled orders
  alerts.log         exit-rule triggers (margin ratio, basis, quota, funding < borrow twice)
  errors.log         failed API calls
  state.json         cursors and cumulative sums

Dry run from anywhere:  OKX_COIN=ATOM python3 -I src/okx_logger.py        (public-only)
Self-test of signing:   python3 -I src/okx_logger.py --selftest
"""
import os, sys, json, csv, time, hmac, base64, hashlib, urllib.request, urllib.parse, datetime as dt

BASE = "https://www.okx.com"
KEY, SECRET, PASS = os.environ.get("OKX_KEY", ""), os.environ.get("OKX_SECRET", ""), os.environ.get("OKX_PASSPHRASE", "")
COIN = os.environ.get("OKX_COIN", "").upper()
LOGDIR = os.path.expanduser(os.environ.get("OKX_LOG_DIR", "~/okx_log"))
SIM = os.environ.get("OKX_SIMULATED", "") == "1"
PRIVATE = bool(KEY and SECRET and PASS)
SWAP, SPOT = f"{COIN}-USDT-SWAP", f"{COIN}-USDT"
NOTIONAL_USDT = float(os.environ.get("OKX_NOTIONAL", "1000"))


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.datetime.now(dt.timezone.utc).microsecond // 1000:03d}Z"


def sign(ts, method, path, body=""):
    msg = f"{ts}{method}{path}{body}"
    return base64.b64encode(hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).digest()).decode()


def log_err(msg):
    os.makedirs(LOGDIR, exist_ok=True)
    with open(os.path.join(LOGDIR, "errors.log"), "a") as f:
        f.write(f"{now_iso()} {msg}\n")


def req(method, path, params=None, private=False):
    """GET/POST to OKX v5. Returns data list or None. 3 attempts, 2/4 s backoff, never raises."""
    q = ("?" + urllib.parse.urlencode(params)) if params and method == "GET" else ""
    body = json.dumps(params) if params and method != "GET" else ""
    for attempt in range(3):
        try:
            h = {"Content-Type": "application/json", "User-Agent": "okx-logger/1.0"}
            if private:
                ts = now_iso()
                h.update({"OK-ACCESS-KEY": KEY, "OK-ACCESS-SIGN": sign(ts, method, path + q, body),
                          "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": PASS})
            if SIM:
                h["x-simulated-trading"] = "1"
            r = urllib.request.Request(BASE + path + q, data=body.encode() if body else None, headers=h, method=method)
            with urllib.request.urlopen(r, timeout=20) as resp:
                d = json.loads(resp.read().decode())
            if d.get("code") == "0":
                return d.get("data", [])
            log_err(f"{path} code={d.get('code')} msg={d.get('msg')}")
            if d.get("code") in ("50111", "50113", "50102"):  # bad key / sig / timestamp: no point retrying
                return None
        except Exception as e:
            log_err(f"{path} attempt {attempt + 1}: {e}")
        time.sleep(2 * (attempt + 1))
    return None


def f(x, default=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def append_csv(name, row, header):
    os.makedirs(LOGDIR, exist_ok=True)
    p = os.path.join(LOGDIR, name)
    new = not os.path.exists(p)
    with open(p, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(header)
        w.writerow(row)


def alert(msg):
    os.makedirs(LOGDIR, exist_ok=True)
    line = f"{now_iso()} ALERT {msg}"
    print(line, flush=True)
    with open(os.path.join(LOGDIR, "alerts.log"), "a") as fh:
        fh.write(line + "\n")


def load_state():
    p = os.path.join(LOGDIR, "state.json")
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            log_err("state.json unreadable, starting fresh")
    return {"last_bill_id": "", "seen_fills": [], "seen_failed": [], "last_funding_ts": 0,
            "cum_funding": 0.0, "cum_interest": 0.0, "cum_fees": 0.0, "fund_below_borrow_streak": 0, "pub_fail_streak": 0, "priv_fail_streak": 0}


def save_state(s):
    os.makedirs(LOGDIR, exist_ok=True)
    s["seen_fills"] = s["seen_fills"][-2000:]
    s["seen_failed"] = s["seen_failed"][-2000:]
    json.dump(s, open(os.path.join(LOGDIR, "state.json"), "w"))


SNAP_HDR = ["ts", "coin", "perp_last", "perp_bid", "perp_ask", "spot_last", "spot_bid", "spot_ask", "basis_pct", "funding_rate", "funding_interval_h",
            "funding_ann_to_long_pct", "next_funding_ts", "borrow_apr_pct", "quota_coin", "borrowed_coin", "interest_accrued_usdt",
            "perp_pos", "perp_avg_px", "perp_upl", "mgn_ratio", "total_eq_usdt", "private", "err"]
INT_HDR = ["ts", "funding_ts", "coin", "funding_received_usdt", "interest_usdt", "funding_rate", "basis_pct", "perp_mark", "spot_last",
           "total_eq_usdt", "cum_funding", "cum_interest", "cum_fees"]
FILL_HDR = ["ts", "fill_ts", "instId", "side", "px", "sz", "fee", "feeCcy", "ordId", "tradeId", "mid_at_log", "note"]
FAIL_HDR = ["ts", "instId", "side", "px", "sz", "state", "ordId", "cTime"]


def main():
    if not COIN:
        print("OKX_COIN not set; nothing to log", file=sys.stderr)
        return 2
    st = load_state()
    ts = now_iso()
    err = []
    # ---------- public ----------
    fr = req("GET", "/api/v5/public/funding-rate", {"instId": SWAP})
    tk_p = req("GET", "/api/v5/market/ticker", {"instId": SWAP})
    tk_s = req("GET", "/api/v5/market/ticker", {"instId": SPOT})
    lq = req("GET", "/api/v5/public/interest-rate-loan-quota")
    if not (fr and tk_p and tk_s):
        err.append("public")
        st["pub_fail_streak"] += 1
    else:
        st["pub_fail_streak"] = 0
    fr0 = (fr or [{}])[0]; p = (tk_p or [{}])[0]; s = (tk_s or [{}])[0]
    rate = f(fr0.get("fundingRate")); ft, nft = f(fr0.get("fundingTime"), 0), f(fr0.get("nextFundingTime"), 0)
    interval_h = (nft - ft) / 3.6e6 if nft and ft else float("nan")
    fund_ann = -rate * (24 / interval_h) * 365 * 100 if interval_h == interval_h and interval_h > 0 else float("nan")
    perp_last, perp_bid, perp_ask = f(p.get("last")), f(p.get("bidPx")), f(p.get("askPx"))
    spot_last, spot_bid, spot_ask = f(s.get("last")), f(s.get("bidPx")), f(s.get("askPx"))
    basis = (perp_last / spot_last - 1) * 100 if spot_last and spot_last == spot_last else float("nan")
    borrow_apr, quota = float("nan"), float("nan")
    if lq:
        for x in lq[0].get("basic", []):
            if x.get("ccy") == COIN:
                borrow_apr, quota = f(x.get("rate")) * 365 * 100, f(x.get("quota"))
    # ---------- private ----------
    borrowed = interest_acc = perp_pos = avg_px = upl = mgn = total_eq = float("nan")
    if PRIVATE:
        bal = req("GET", "/api/v5/account/balance", private=True)
        pos = req("GET", "/api/v5/account/positions", {"instId": SWAP}, private=True)
        acc = req("GET", "/api/v5/account/interest-accrued", {"ccy": COIN}, private=True)
        if bal is None or pos is None:
            err.append("private")
            st["priv_fail_streak"] += 1
        else:
            st["priv_fail_streak"] = 0
            b0 = bal[0] if bal else {}
            total_eq = f(b0.get("totalEq"))
            for d in b0.get("details", []):
                if d.get("ccy") == COIN:
                    borrowed = f(d.get("liab"), 0.0)
                    interest_acc = f(d.get("interest"), 0.0) * spot_last if spot_last == spot_last else float("nan")
            for q in pos or []:
                if q.get("instId") == SWAP:
                    perp_pos, avg_px, upl, mgn = f(q.get("pos")), f(q.get("avgPx")), f(q.get("upl")), f(q.get("mgnRatio"))
        if acc:
            try:
                interest_acc = sum(f(a.get("interest"), 0.0) for a in acc[:50]) * (spot_last if spot_last == spot_last else 0)
            except Exception:
                pass
        # bills: funding fee (type 8) and interest deduction (type 7)
        new_funding = new_interest = 0.0
        for btype in ("8", "7"):
            bills = req("GET", "/api/v5/account/bills", {"type": btype, "limit": "100"}, private=True) or []
            for b in sorted(bills, key=lambda x: int(x.get("billId", 0))):
                if int(b.get("billId", 0)) <= int(st["last_bill_id"] or 0):
                    continue
                if b.get("ccy") not in ("USDT", COIN):
                    continue
                amt = f(b.get("pnl") if btype == "8" else b.get("balChg"), 0.0)
                if b.get("ccy") == COIN and spot_last == spot_last:
                    amt *= spot_last
                if btype == "8":
                    new_funding += amt
                else:
                    new_interest += amt
            if bills:
                st["last_bill_id"] = str(max(int(st["last_bill_id"] or 0), max(int(x.get("billId", 0)) for x in bills)))
        st["cum_funding"] += new_funding
        st["cum_interest"] += abs(new_interest)
        # fills
        mids = {SWAP: (perp_bid + perp_ask) / 2 if perp_bid == perp_bid else perp_last, SPOT: (spot_bid + spot_ask) / 2 if spot_bid == spot_bid else spot_last}
        for inst, itype in ((SWAP, "SWAP"), (SPOT, "SPOT")):
            fills = req("GET", "/api/v5/trade/fills", {"instType": itype, "instId": inst, "limit": "100"}, private=True) or []
            for x in sorted(fills, key=lambda z: int(z.get("ts", 0))):
                tid = x.get("tradeId")
                if not tid or tid in st["seen_fills"]:
                    continue
                st["seen_fills"].append(tid)
                fee = f(x.get("fee"), 0.0)
                fee_usdt = fee if x.get("feeCcy") == "USDT" else fee * f(x.get("fillPx"), 0.0)
                st["cum_fees"] += abs(fee_usdt)
                append_csv("fills.csv", [ts, x.get("ts"), inst, x.get("side"), x.get("fillPx"), x.get("fillSz"), x.get("fee"), x.get("feeCcy"),
                                         x.get("ordId"), tid, mids[inst], ""], FILL_HDR)
            hist = req("GET", "/api/v5/trade/orders-history", {"instType": itype, "instId": inst, "state": "canceled", "limit": "100"}, private=True) or []
            for o in hist:
                oid = o.get("ordId")
                if not oid or oid in st["seen_failed"] or f(o.get("accFillSz"), 0.0) > 0:
                    continue
                st["seen_failed"].append(oid)
                append_csv("orders_failed.csv", [ts, inst, o.get("side"), o.get("px"), o.get("sz"), o.get("state"), oid, o.get("cTime")], FAIL_HDR)
        # interval row when a funding timestamp has passed since the last logged one
        if ft and ft > st["last_funding_ts"]:
            if st["last_funding_ts"]:
                append_csv("intervals.csv", [ts, int(ft), COIN, round(new_funding, 6), round(abs(new_interest), 6), rate, round(basis, 4), perp_last, spot_last,
                                             total_eq, round(st["cum_funding"], 6), round(st["cum_interest"], 6), round(st["cum_fees"], 6)], INT_HDR)
                # exit rule: funding to longs below borrow APR for 2 consecutive intervals
                if fund_ann == fund_ann and borrow_apr == borrow_apr:
                    st["fund_below_borrow_streak"] = st["fund_below_borrow_streak"] + 1 if fund_ann < borrow_apr else 0
                    if st["fund_below_borrow_streak"] >= 2:
                        alert(f"{COIN}: funding to longs {fund_ann:.0f}%/yr < borrow {borrow_apr:.0f}%/yr for 2 intervals -> EXIT RULE")
            st["last_funding_ts"] = ft
    # ---------- snapshot + alerts ----------
    append_csv("snapshots.csv", [ts, COIN, perp_last, perp_bid, perp_ask, spot_last, spot_bid, spot_ask, round(basis, 4), rate, round(interval_h, 2),
                                 round(fund_ann, 2), int(nft), round(borrow_apr, 2), quota, borrowed, interest_acc, perp_pos, avg_px, upl, mgn, total_eq,
                                 int(PRIVATE), ";".join(err)], SNAP_HDR)
    if basis == basis and abs(basis) > 2:
        alert(f"{COIN}: |basis| {basis:.2f}% > 2%")
    if mgn == mgn and mgn < 3:
        alert(f"{COIN}: perp margin ratio {mgn:.2f} < 3.0 (300%)")
    if quota == quota and borrowed == borrowed and borrowed > 0 and quota < borrowed:
        alert(f"{COIN}: borrow quota {quota} < borrowed {borrowed}")
    if st["pub_fail_streak"] >= 3:
        alert("public API failing 3 runs in a row")
    if st["priv_fail_streak"] >= 3:
        alert("private API failing 3 runs in a row (key / IP whitelist?)")
    save_state(st)
    print(f"{ts} {COIN} perp {perp_last} spot {spot_last} basis {basis:.3f}% funding->long {fund_ann:.0f}%/yr borrow {borrow_apr:.0f}%/yr "
          f"private={'ok' if PRIVATE and 'private' not in err else ('off' if not PRIVATE else 'FAIL')} eq={total_eq}", flush=True)
    return 0


def selftest():
    """Signing check against the OKX docs example shape (prehash = ts + method + path + body)."""
    global SECRET
    SECRET = "22582BD0CFF14C41EDBF1AB98506286D"
    ts = "2020-12-08T09:08:57.715Z"
    sig = sign(ts, "GET", "/api/v5/account/balance?ccy=BTC", "")
    # reference computed with the same formula; guards against accidental changes to the prehash order
    import hashlib as _h
    ref = base64.b64encode(hmac.new(SECRET.encode(), f"{ts}GET/api/v5/account/balance?ccy=BTC".encode(), _h.sha256).digest()).decode()
    print("sign ok" if sig == ref else "sign MISMATCH")
    return 0 if sig == ref else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
