#!/usr/bin/env python3
"""T18 live test bot — Kalshi BTC 15m, CRSI(2,2,75) + head-start signal, taker buy YES at minute 1.

Signal (all known at the window open T, from Binance public mirror data-api.binance.vision):
  crsi_prev = CRSI(2,2,75) of 15-minute closes up to the candle that closed at T          (<= CRSI_MAX, default 20)
  hs        = open price of the 1-m candle starting at T / VWAP of the 1-m candle [T-60s, T) - 1, in bp   (> HS_MIN, default 0)
Action at T + 60 s + LAT: buy YES on the Kalshi market whose open_time == T, limit at the best ask (cents, rounded up),
COUNT contracts, cancel if unfilled after FILL_WAIT s. Hold to settlement. Log everything.

Modes:  --paper (default)  no orders; logs the ask that would have been hit.     --live   places orders.
Env (deploy/kalshi_bot.env.example): KALSHI_KEY_ID, KALSHI_PRIVATE_KEY_PATH (PEM), BOT_LOG_DIR, COUNT, CRSI_MAX, HS_MIN, LAT, FILL_WAIT,
     MAX_DAILY_LOSS_USD, MAX_OPEN, KILL_FILE (touch it to stop trading, logging continues).
Dependencies: python3 >= 3.10, `pip install cryptography` (RSA-PSS signing). No other packages.
Run:  python3 src/kalshi_live/bot.py --paper        (systemd unit in deploy/kalshi-bot.service)
"""
import os, sys, csv, json, time, base64, hashlib, datetime as dt, urllib.request, urllib.parse, math

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
BIN = "https://data-api.binance.vision/api/v3"
SERIES = os.environ.get("SERIES", "KXBTC15M"); SYMBOL = os.environ.get("SYMBOL", "BTCUSDT")
LOGDIR = os.path.expanduser(os.environ.get("BOT_LOG_DIR", "~/kalshi_bot"))
COUNT = int(os.environ.get("COUNT", "20")); CRSI_MAX = float(os.environ.get("CRSI_MAX", "20")); HS_MIN = float(os.environ.get("HS_MIN", "0"))
LAT = float(os.environ.get("LAT", "2")); FILL_WAIT = float(os.environ.get("FILL_WAIT", "20"))
MAX_DAILY_LOSS = float(os.environ.get("MAX_DAILY_LOSS_USD", "30")); MAX_OPEN = int(os.environ.get("MAX_OPEN", "4"))
KILL_FILE = os.environ.get("KILL_FILE", os.path.join(LOGDIR, "KILL"))
LIVE = "--live" in sys.argv
KEY_ID = os.environ.get("KALSHI_KEY_ID", ""); PEM = os.environ.get("KALSHI_PRIVATE_KEY_PATH", "")

# ---------------- utilities ----------------
def now(): return dt.datetime.now(dt.timezone.utc)
def log(msg):
    os.makedirs(LOGDIR, exist_ok=True); line = f"{now().isoformat(timespec='seconds')} {msg}"; print(line, flush=True)
    with open(os.path.join(LOGDIR, "bot.log"), "a") as f: f.write(line + "\n")
def csv_append(name, row, header):
    os.makedirs(LOGDIR, exist_ok=True); p = os.path.join(LOGDIR, name); new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(header)
        w.writerow(row)
def http(url, headers=None, data=None, method=None, timeout=15):
    r = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "t18-bot/1.0"}, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp: return json.loads(resp.read().decode())
def retry(fn, tries=3, wait=1.0, what=""):
    for i in range(tries):
        try: return fn()
        except Exception as e:
            log(f"ERR {what}: {e}"); time.sleep(wait * (i + 1))
    return None

# ---------------- Kalshi auth (RSA-PSS, SHA256 over timestamp_ms + METHOD + path) ----------------
_priv = None
def kalshi_headers(method, path):
    global _priv
    if _priv is None:
        from cryptography.hazmat.primitives import serialization
        _priv = serialization.load_pem_private_key(open(PEM, "rb").read(), password=None)
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    ts = str(int(time.time() * 1000)); msg = (ts + method + "/trade-api/v2" + path).encode()
    sig = _priv.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": KEY_ID, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(), "KALSHI-ACCESS-TIMESTAMP": ts,
            "Content-Type": "application/json", "User-Agent": "t18-bot/1.0"}
def kalshi(method, path, params=None, body=None, auth=False):
    q = ("?" + urllib.parse.urlencode(params)) if params else ""
    h = kalshi_headers(method, path) if auth else {"User-Agent": "t18-bot/1.0"}
    return http(KALSHI + path + q, headers=h, data=json.dumps(body).encode() if body else None, method=method)

# ---------------- signal ----------------
def rma(xs, n):
    out = []; a = None
    for x in xs:
        a = x if a is None else (a * (n - 1) + x) / n; out.append(a)
    return out
def rsi(xs, n):
    ch = [xs[i] - xs[i - 1] for i in range(1, len(xs))]; u = [max(c, 0) for c in ch]; d = [max(-c, 0) for c in ch]
    ru, rd = rma(u, n), rma(d, n)
    return [float("nan")] + [100.0 if b == 0 else 100 - 100 / (1 + a / b) for a, b in zip(ru, rd)]
def streak(xs):
    s = [0.0]
    for i in range(1, len(xs)):
        if xs[i] == xs[i - 1]: s.append(0.0)
        elif xs[i] > xs[i - 1]: s.append(1.0 if s[-1] <= 0 else s[-1] + 1)
        else: s.append(-1.0 if s[-1] >= 0 else s[-1] - 1)
    return s
def crsi_last(closes, a=2, b=2, c=75):
    """CRSI of the LAST close in the list (same definition as src/analyze.py)."""
    r1 = rsi(closes, a)[-1]; r2 = rsi(streak(closes), b)[-1]
    roc = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    cur = roc[-1]; prev = roc[-1 - c:-1]
    pr = sum(1 for x in prev if x <= cur) / c * 100
    return (r1 + r2 + pr) / 3
def binance_15m_closes(n=400):
    d = http(f"{BIN}/klines?symbol={SYMBOL}&interval=15m&limit={n}")
    return [(int(k[0]) // 1000, float(k[4])) for k in d]   # (open_ts, close) ; last one may be the CURRENT (unclosed) candle
def binance_1m(start_ts, n=2):
    d = http(f"{BIN}/klines?symbol={SYMBOL}&interval=1m&startTime={start_ts * 1000}&limit={n}")
    return [dict(t=int(k[0]) // 1000, o=float(k[1]), c=float(k[4]), v=float(k[5]), qv=float(k[7]), closed=int(k[6]) // 1000 < time.time()) for k in d]
def compute_signal(T):
    """T = window open (unix s, multiple of 900). Returns dict or None (data not ready)."""
    ks = retry(lambda: binance_15m_closes(), what="binance 15m")
    if not ks: return None
    closes = [c for t, c in ks if t + 900 <= T]            # only candles that CLOSED at or before T
    if len(closes) < 120 or ks[-1][0] not in (T, T - 900): return None
    crsi = crsi_last(closes)
    m = retry(lambda: binance_1m(T - 60, 2), what="binance 1m")
    if not m or len(m) < 2 or m[0]["t"] != T - 60 or m[1]["t"] != T: return None
    pre = m[0]; vwap = pre["qv"] / pre["v"] if pre["v"] > 0 else pre["c"]
    hs = (m[1]["o"] / vwap - 1) * 1e4
    return dict(crsi=crsi, hs=hs, vwap_pre=vwap, open_px=m[1]["o"], signal=(crsi <= CRSI_MAX) and (hs > HS_MIN))

# ---------------- Kalshi market / orders ----------------
def market_for_open(T):
    iso = dt.datetime.fromtimestamp(T, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d = retry(lambda: kalshi("GET", "/markets", {"series_ticker": SERIES, "status": "open", "limit": 20}), what="kalshi markets")
    for m in (d or {}).get("markets", []):
        if m.get("open_time") == iso: return m
    return None
def best_ask(ticker):
    """Kalshi orderbook (orderbook_fp): no_dollars / yes_dollars = resting bids [price, qty]. Best YES ask = 1 - best NO bid. Returns cents (ceil), qty, best yes bid cents."""
    d = retry(lambda: kalshi("GET", f"/markets/{ticker}/orderbook", {"depth": 10}), what="orderbook")
    ob = (d or {}).get("orderbook_fp") or (d or {}).get("orderbook") or {}
    no_b = ob.get("no_dollars") or ob.get("no") or []; yes_b = ob.get("yes_dollars") or ob.get("yes") or []
    if not no_b: return None, None, None
    scale = 1.0 if "no_dollars" in ob else 0.01
    best_no = max(no_b, key=lambda x: float(x[0])); ask = 1 - float(best_no[0]) * scale; ask_qty = float(best_no[1])
    bid_c = math.ceil(max(float(x[0]) for x in yes_b) * scale * 100 - 1e-9) if yes_b else None
    return math.ceil(ask * 100 - 1e-9), ask_qty, bid_c
def place_taker_yes(ticker, price_c, count):
    body = {"ticker": ticker, "action": "buy", "side": "yes", "type": "limit", "count": count, "yes_price": int(price_c), "client_order_id": f"t18-{ticker}-{int(time.time())}"}
    return retry(lambda: kalshi("POST", "/portfolio/orders", body=body, auth=True), what="place order")
def order_status(order_id): return retry(lambda: kalshi("GET", f"/portfolio/orders/{order_id}", auth=True), what="order status")
def cancel(order_id): return retry(lambda: kalshi("DELETE", f"/portfolio/orders/{order_id}", auth=True), what="cancel")

# ---------------- state / risk ----------------
STATE = os.path.join(LOGDIR, "state.json")
def load_state():
    try: return json.load(open(STATE))
    except Exception: return {"open": {}, "done": {}, "day": "", "day_pnl": 0.0}
def save_state(s): os.makedirs(LOGDIR, exist_ok=True); json.dump(s, open(STATE, "w"))
def reconcile(s):
    """Fetch results for open positions whose market has settled; book PnL."""
    for tk, pos in list(s["open"].items()):
        m = retry(lambda: kalshi("GET", f"/markets/{tk}"), what="market result")
        mk = (m or {}).get("market") or {}
        if mk.get("result") in ("yes", "no"):
            win = 1 if mk["result"] == "yes" else 0; px = pos["fill_px"] / 100; fee = math.ceil(0.07 * px * (1 - px) * 100) / 100 if pos["count"] else 0
            pnl = pos["count"] * (win - px - fee); pos.update(result=mk["result"], pnl=round(pnl, 4)); s["done"][tk] = pos; del s["open"][tk]
            d = now().strftime("%Y-%m-%d")
            if s["day"] != d: s["day"], s["day_pnl"] = d, 0.0
            s["day_pnl"] += pnl
            csv_append("settled.csv", [now().isoformat(timespec="seconds"), tk, pos["count"], pos["fill_px"], mk["result"], round(pnl, 4), round(s["day_pnl"], 2)],
                       ["ts", "ticker", "count", "fill_px_c", "result", "pnl_usd", "day_pnl_usd"])
            log(f"SETTLED {tk} {mk['result']} fill {pos['fill_px']}c x{pos['count']} pnl {pnl:+.2f} day {s['day_pnl']:+.2f}")
SIG_HDR = ["ts", "window_open_utc", "ticker", "crsi_prev", "hs_bp", "open_px", "vwap_pre", "signal", "ask_c", "ask_qty", "bid_c", "mode", "order_id", "filled", "fill_px_c", "note"]

# ---------------- main loop ----------------
def main():
    log(f"start mode={'LIVE' if LIVE else 'PAPER'} series={SERIES} count={COUNT} crsi<= {CRSI_MAX} hs> {HS_MIN} lat={LAT}s")
    if LIVE and not (KEY_ID and PEM and os.path.exists(PEM)): log("LIVE requested but KALSHI_KEY_ID / KALSHI_PRIVATE_KEY_PATH missing"); return 2
    s = load_state(); last_T = 0
    while True:
        t = time.time(); T = int(t // 900) * 900           # current window open
        if T != last_T and t - T >= 61 + LAT:                # minute 1 passed: act once per window
            last_T = T
            if t - T > 90: log(f"window {T}: started late ({t - T:.0f}s in), skip"); continue
            try:
                reconcile(s)
                sig = compute_signal(T)
                if sig is None: log(f"window {T}: signal data not ready, skip"); csv_append("signals.csv", [now().isoformat(timespec='seconds'), T, "", "", "", "", "", "", "", "", "", "paper" if not LIVE else "live", "", 0, "", "nodata"], SIG_HDR); save_state(s); continue
                mk = market_for_open(T); tk = mk["ticker"] if mk else ""
                ask_c, ask_qty, bid_c = best_ask(tk) if tk else (None, None, None)
                note = ""; filled = 0; fill_px = ""; oid = ""
                blocked = os.path.exists(KILL_FILE) or s.get("day_pnl", 0) <= -MAX_DAILY_LOSS or len(s["open"]) >= MAX_OPEN
                if sig["signal"] and tk and ask_c is not None and not blocked and ask_c <= 70:
                    if LIVE:
                        r = place_taker_yes(tk, ask_c, COUNT); oid = ((r or {}).get("order") or {}).get("order_id", "")
                        deadline = time.time() + FILL_WAIT
                        while oid and time.time() < deadline:
                            st = (order_status(oid) or {}).get("order") or {}
                            filled = int(st.get("fill_count") or st.get("taker_fill_count") or 0) + int(st.get("maker_fill_count") or 0)
                            if st.get("status") in ("executed", "canceled") or filled >= COUNT: break
                            time.sleep(1)
                        if oid and filled < COUNT: cancel(oid)
                        if filled: fill_px = ask_c; s["open"][tk] = dict(count=filled, fill_px=ask_c, T=T); note = "live"
                        else: note = "unfilled"
                    else:
                        filled = min(COUNT, ask_qty or COUNT); fill_px = ask_c; s["open"][tk] = dict(count=filled, fill_px=ask_c, T=T); note = "paper"
                elif sig["signal"]:
                    note = "blocked:" + ("kill" if os.path.exists(KILL_FILE) else "dayloss" if s.get("day_pnl", 0) <= -MAX_DAILY_LOSS else "maxopen" if len(s["open"]) >= MAX_OPEN else "no-market/ask" if ask_c is None else "ask>70")
                csv_append("signals.csv", [now().isoformat(timespec="seconds"), T, tk, round(sig["crsi"], 2), round(sig["hs"], 2), sig["open_px"], round(sig["vwap_pre"], 2),
                                           int(sig["signal"]), ask_c, ask_qty, bid_c, "live" if LIVE else "paper", oid, filled, fill_px, note], SIG_HDR)
                log(f"window {dt.datetime.fromtimestamp(T, dt.timezone.utc):%H:%M} {tk} crsi {sig['crsi']:.1f} hs {sig['hs']:+.1f}bp signal={int(sig['signal'])} ask {ask_c} x{ask_qty} -> {note or 'no trade'} filled {filled}")
                save_state(s)
            except Exception as e:
                log(f"ERR loop: {e}")
        time.sleep(0.5)

def selftest():
    """Signal sanity: compute for the most recent completed window and print; no orders."""
    T = int(time.time() // 900) * 900
    if time.time() - T < 63: print(f"wait {63 - (time.time() - T):.0f}s for minute 1 of the current window"); time.sleep(63 - (time.time() - T))
    sig = compute_signal(T); print("window", dt.datetime.fromtimestamp(T, dt.timezone.utc), sig)
    mk = market_for_open(T); print("market", (mk or {}).get("ticker"), (mk or {}).get("open_time"))
    if mk: print("best ask/qty/bid", best_ask(mk["ticker"]))
    return 0

if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
