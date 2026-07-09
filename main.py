import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import websockets
import requests
import os

# Hello :)
app = FastAPI()

STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", "150"))
BET_PERCENT = float(os.getenv("BET_PERCENT", "2"))
MAX_BET_CAP = float(os.getenv("MAX_BET_CAP", "100"))
LIMIT_PRICE = float(os.getenv("LIMIT_PRICE", "0.5"))
RESOLVE_SECONDS = 900
LARGE_TRADE_USD = 50000

state = {}
state["best_bid"] = None
state["best_ask"] = None
state["cvd"] = 0.0
state["last_signal"] = None
state["last_decision"] = None
state["last_filter_reason"] = None
state["filtered"] = 0
state["bankroll"] = STARTING_BANKROLL
state["wins"] = 0
state["losses"] = 0
state["net_profit"] = 0.0
state["trades"] = []
state["pending"] = []
state["ob_imbalance"] = None
state["trade_events"] = []
state["large_trade_count_1m"] = 0
state["avg_trade_usd_1m"] = 0.0
state["liquidations"] = []
state["liq_count_5m"] = 0
state["liq_buy_5m"] = 0
state["liq_sell_5m"] = 0
state["funding_rate"] = None
state["next_funding_time"] = None
state["open_interest"] = None
state["open_interest_prev"] = None
state["oi_delta"] = None

def mid_price():
    if state["best_bid"] is None or state["best_ask"] is None:
        return None
    return (state["best_bid"] + state["best_ask"]) / 2.0

async def binance_orderbook_listener():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            state["best_bid"] = float(data["b"])
            state["best_ask"] = float(data["a"])

async def binance_depth_listener():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@depth5@100ms"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            bid_vol = sum(float(b[1]) for b in bids)
            ask_vol = sum(float(a[1]) for a in asks)
            total = bid_vol + ask_vol
            if total > 0:
                state["ob_imbalance"] = round((bid_vol - ask_vol) / total, 4)

async def binance_trades_listener():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            qty = float(data["q"])
            px = float(data["p"])
            is_buyer_maker = data["m"]
            delta = -qty if is_buyer_maker else qty
            state["cvd"] += delta
            now = time.time()
            state["trade_events"].append((now, qty * px))
            cutoff = now - 60
            state["trade_events"] = [e for e in state["trade_events"] if e[0] > cutoff]
            usd_sizes = [e[1] for e in state["trade_events"]]
            large_count = 0
            for s in usd_sizes:
                if s >= LARGE_TRADE_USD:
                    large_count = large_count + 1
            state["large_trade_count_1m"] = large_count
            if len(usd_sizes) > 0:
                state["avg_trade_usd_1m"] = round(sum(usd_sizes) / len(usd_sizes), 2)

async def binance_liquidation_listener():
    uri = "wss://fstream.binance.com/ws/btcusdt@forceOrder"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            order = data.get("o", {})
            side = order.get("S")
            qty = float(order.get("q", 0))
            px = float(order.get("p", 0))
            now = time.time()
            event = {"time": now, "side": side, "qty": qty, "price": px}
            state["liquidations"].insert(0, event)
            state["liquidations"] = state["liquidations"][:100]
            cutoff = now - 300
            recent = [e for e in state["liquidations"] if e["time"] > cutoff]
            state["liq_count_5m"] = len(recent)
            buy_count = 0
            sell_count = 0
            for e in recent:
                if e["side"] == "BUY":
                    buy_count = buy_count + 1
                else:
                    sell_count = sell_count + 1
            state["liq_buy_5m"] = buy_count
            state["liq_sell_5m"] = sell_count
            notify_telegram("LIQUIDATION " + str(side) + " $" + str(round(qty * px, 0)) + " @ " + str(px))

async def binance_mark_price_listener():
    uri = "wss://fstream.binance.com/ws/btcusdt@markPrice@1s"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            state["funding_rate"] = float(data.get("r", 0))
            state["next_funding_time"] = data.get("T")

async def open_interest_poller():
    while True:
        try:
            resp = await asyncio.to_thread(requests.get, "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", None, 10)
        except Exception:
            resp = None
        if resp is not None:
            try:
                data = resp.json()
                new_oi = float(data.get("openInterest", 0))
                if state["open_interest"] is not None:
                    state["open_interest_prev"] = state["open_interest"]
                    state["oi_delta"] = round(new_oi - state["open_interest_prev"], 2)
                state["open_interest"] = new_oi
            except Exception:
                pass
        await asyncio.sleep(60)

@app.on_event("startup")
async def start_listeners():
    asyncio.create_task(binance_orderbook_listener())
    asyncio.create_task(binance_depth_listener())
    asyncio.create_task(binance_trades_listener())
    asyncio.create_task(binance_liquidation_listener())
    asyncio.create_task(binance_mark_price_listener())
    asyncio.create_task(open_interest_poller())

def orderbook_confirms(direction):
    if state["best_bid"] is None or state["best_ask"] is None:
        state["last_filter_reason"] = "no price data yet"
        return False
    spread = state["best_ask"] - state["best_bid"]
    if spread > 5:
        state["last_filter_reason"] = "spread too wide: " + str(round(spread, 2))
        return False
    if direction == "Up" and state["cvd"] > 0:
        state["last_filter_reason"] = "confirmed: CVD positive"
        return True
    if direction == "Down" and state["cvd"] < 0:
        state["last_filter_reason"] = "confirmed: CVD negative"
        return True
    state["last_filter_reason"] = "CVD disagreed, value: " + str(round(state["cvd"], 1))
    return False

async def resolve_trade(direction, entry_price, signal_time):
    pending_entry = {"direction": direction, "entry_price": entry_price, "signal_time": signal_time, "resolve_time": signal_time + RESOLVE_SECONDS}
    state["pending"].append(pending_entry)
    await asyncio.sleep(RESOLVE_SECONDS)
    exit_price = mid_price()
    state["pending"] = [p for p in state["pending"] if p is not pending_entry]
    if exit_price is None:
        return
    won = (direction == "Up" and exit_price >= entry_price) or (direction == "Down" and exit_price < entry_price)
    fraction = state["bankroll"] * BET_PERCENT / 100.0
    bet_amount = min(fraction, MAX_BET_CAP)
    contracts = bet_amount / LIMIT_PRICE
    if won:
        pnl = (1.0 - LIMIT_PRICE) * contracts
        state["bankroll"] = state["bankroll"] + pnl
        state["wins"] = state["wins"] + 1
    else:
        pnl = -bet_amount
        state["bankroll"] = state["bankroll"] + pnl
        state["losses"] = state["losses"] + 1
    state["net_profit"] = state["net_profit"] + pnl
    record = {}
    record["direction"] = direction
    record["entry_price"] = entry_price
    record["exit_price"] = exit_price
    record["won"] = won
    record["bet_amount"] = round(bet_amount, 2)
    record["pnl"] = round(pnl, 2)
    record["bankroll_after"] = round(state["bankroll"], 2)
    record["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(signal_time))
    state["trades"].insert(0, record)
    state["trades"] = state["trades"][:200]
    outcome_text = "WIN" if won else "LOSS"
    msg = outcome_text + " | " + direction + " | PnL: $" + str(round(pnl, 2)) + " | Bankroll: $" + str(round(state["bankroll"], 2))
    notify_telegram(msg)

@app.post("/tv-signal")
async def tv_signal(request: Request):
    payload = await request.json()
    direction = payload.get("direction")
    now = time.time()
    state["last_signal"] = {"direction": direction, "time": now}
    confirmed = orderbook_confirms(direction)
    if confirmed:
        decision = "TRADE"
        entry_price = mid_price()
        if entry_price is not None:
            asyncio.create_task(resolve_trade(direction, entry_price, now))
    else:
        decision = "FILTERED"
        state["filtered"] = state["filtered"] + 1
    state["last_decision"] = decision
    msg = "Signal: " + str(direction) + " | Decision: " + decision + " | Reason: " + str(state["last_filter_reason"])
    notify_telegram(msg)
    return {"status": "ok", "decision": decision, "reason": state["last_filter_reason"]}

def notify_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception:
        pass

@app.get("/stats")
async def stats():
    total = state["wins"] + state["losses"]
    win_rate = (state["wins"] / total * 100.0) if total > 0 else None
    growth_x = (state["bankroll"] / STARTING_BANKROLL) if STARTING_BANKROLL > 0 else None
    equity_curve = []
    running = 0.0
    for t in reversed(state["trades"]):
        running = running + t["pnl"]
        equity_curve.append(round(running, 2))
    out = {}
    out["best_bid"] = state["best_bid"]
    out["best_ask"] = state["best_ask"]
    out["cvd"] = round(state["cvd"], 1)
    out["ob_imbalance"] = state["ob_imbalance"]
    out["large_trade_count_1m"] = state["large_trade_count_1m"]
    out["avg_trade_usd_1m"] = state["avg_trade_usd_1m"]
    out["liq_count_5m"] = state["liq_count_5m"]
    out["liq_buy_5m"] = state["liq_buy_5m"]
    out["liq_sell_5m"] = state["liq_sell_5m"]
    out["funding_rate"] = state["funding_rate"]
    out["open_interest"] = state["open_interest"]
    out["oi_delta"] = state["oi_delta"]
    out["last_signal"] = state["last_signal"]
    out["last_decision"] = state["last_decision"]
    out["last_filter_reason"] = state["last_filter_reason"]
    out["filtered"] = state["filtered"]
    out["wins"] = state["wins"]
    out["losses"] = state["losses"]
    out["win_rate"] = win_rate
    out["net_profit"] = round(state["net_profit"], 2)
    out["starting_bankroll"] = STARTING_BANKROLL
    out["bankroll"] = round(state["bankroll"], 2)
    out["growth_x"] = growth_x
    out["pending_count"] = len(state["pending"])
    out["recent_trades"] = state["trades"][:20]
    out["equity_curve"] = equity_curve
    return out

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = "<html><body style='background:#0a0a0a;color:#eee;font-family:monospace;padding:20px'>"
    html = html + "<h2>CRSI + HTF TREND - LIVE STATS</h2><table id='t'></table>"
    html = html + "<h2>Data Layers (logging only, not yet used in decisions)</h2><table id='layers'></table>"
    html = html + "<h2>Equity Curve</h2><canvas id='c' width='600' height='200' style='background:#111;border:1px solid #222'></canvas>"
    html = html + "<h2>Recent Trades</h2><div id='tr'></div>"
    html = html + "<script>"
    html = html + "function row(a,b){return '<tr><td style=\"color:#999;padding:4px\">'+a+'</td><td style=\"color:#fff;padding:4px;text-align:right\">'+b+'</td></tr>';}"
    html = html + "async function r(){const res=await fetch('/stats');const d=await res.json();"
    html = html + "let t='';"
    html = html + "t+=row('Best Bid',d.best_bid);"
    html = html + "t+=row('Best Ask',d.best_ask);"
    html = html + "t+=row('CVD',d.cvd);"
    html = html + "t+=row('Last Signal',d.last_signal?d.last_signal.direction:'-');"
    html = html + "t+=row('Last Decision',d.last_decision||'-');"
    html = html + "t+=row('Filter Reason',d.last_filter_reason||'-');"
    html = html + "t+=row('Filtered',d.filtered);"
    html = html + "t+=row('Pending',d.pending_count);"
    html = html + "t+=row('Wins',d.wins);"
    html = html + "t+=row('Losses',d.losses);"
    html = html + "t+=row('Win Rate',d.win_rate!==null?d.win_rate.toFixed(2)+'%':'n/a');"
    html = html + "t+=row('Net Profit','$'+d.net_profit);"
    html = html + "t+=row('Starting Bankroll','$'+d.starting_bankroll);"
    html = html + "t+=row('Current Bankroll','$'+d.bankroll);"
    html = html + "t+=row('Growth',d.growth_x!==null?d.growth_x.toFixed(2)+'x':'n/a');"
    html = html + "document.getElementById('t').innerHTML=t;"
    html = html + "let l='';"
    html = html + "l+=row('Order Book Imbalance',d.ob_imbalance!==null?d.ob_imbalance:'n/a');"
    html = html + "l+=row('Large Trades (1m, >$50k)',d.large_trade_count_1m);"
    html = html + "l+=row('Avg Trade Size (1m, $)',d.avg_trade_usd_1m);"
    html = html + "l+=row('Liquidations (5m)',d.liq_count_5m);"
    html = html + "l+=row('Liq Buy-side (5m)',d.liq_buy_5m);"
    html = html + "l+=row('Liq Sell-side (5m)',d.liq_sell_5m);"
    html = html + "l+=row('Funding Rate',d.funding_rate!==null?(d.funding_rate*100).toFixed(4)+'%':'n/a');"
    html = html + "l+=row('Open Interest (BTC)',d.open_interest!==null?d.open_interest.toFixed(2):'n/a');"
    html = html + "l+=row('OI Delta (last poll)',d.oi_delta!==null?d.oi_delta:'n/a');"
    html = html + "document.getElementById('layers').innerHTML=l;"
    html = html + "document.getElementById('tr').innerHTML=d.recent_trades.map(x=>'<div style=\"padding:3px 0\"><span style=\"color:'+(x.won?'#4caf50':'#f44336')+'\">'+(x.won?'WIN':'LOSS')+'</span> '+x.direction+' PnL $'+x.pnl+' Bankroll $'+x.bankroll_after+' '+x.time+'</div>').join('')||'No trades yet';"
    html = html + "const pts=d.equity_curve;const cv=document.getElementById('c');const ctx=cv.getContext('2d');ctx.clearRect(0,0,600,200);"
    html = html + "if(pts.length>1){const mn=Math.min(...pts,0);const mx=Math.max(...pts,0);const rg=(mx-mn)||1;ctx.beginPath();ctx.strokeStyle='#4dd0e1';ctx.lineWidth=2;pts.forEach((p,i)=>{const x=i*(600/(pts.length-1));const y=200-((p-mn)/rg)*180-10;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();}}"
    html = html + "r();setInterval(r,3000);"
    html = html + "</script></body></html>"
    return html
