import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import websockets
import requests
import os

app = FastAPI()

STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", "150"))
BET_PERCENT = float(os.getenv("BET_PERCENT", "2"))
MAX_BET_CAP = float(os.getenv("MAX_BET_CAP", "100"))
LIMIT_PRICE = float(os.getenv("LIMIT_PRICE", "0.5"))
RESOLVE_SECONDS = 900

state = {"best_bid": None, "best_ask": None, "cvd": 0.0, "last_signal": None, "last_decision": None, "filtered": 0, "bankroll": STARTING_BANKROLL, "wins": 0, "losses": 0, "net_profit": 0.0, "trades": [], "pending": []}

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

async def binance_trades_listener():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            qty = float(data["q"])
            is_buyer_maker = data["m"]
            delta = -qty if is_buyer_maker else qty
            state["cvd"] += delta

@app.on_event("startup")
async def start_listeners():
    asyncio.create_task(binance_orderbook_listener())
    asyncio.create_task(binance_trades_listener())

def orderbook_confirms(direction):
    if state["best_bid"] is None or state["best_ask"] is None:
        return False
    spread = state["best_ask"] - state["best_bid"]
    if spread > 5:
        return False
    if direction == "Up" and state["cvd"] > 0:
        return True
    if direction == "Down" and state["cvd"] < 0:
        return True
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
    record = {"direction": direction, "entry_price": entry_price, "exit_price": exit_price, "won": won, "bet_amount": round(bet_amount, 2), "pnl": round(pnl, 2), "bankroll_after": round(state["bankroll"], 2), "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(signal_time))}
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
    if orderbook_confirms(direction):
        decision = "TRADE"
        entry_price = mid_price()
        if entry_price is not None:
            asyncio.create_task(resolve_trade(direction, entry_price, now))
    else:
        decision = "FILTERED"
        state["filtered"] = state["filtered"] + 1
    state["last_decision"] = decision
    msg = "Signal: " + str(direction) + " | Decision: " + decision + " | CVD: " + str(round(state["cvd"], 1))
    notify_telegram(msg)
    return {"status": "ok", "decision": decision}

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
    return {"best_bid": state["best_bid"], "best_ask": state["best_ask"], "cvd": round(state["cvd"], 1), "last_signal": state["last_signal"], "last_decision": state["last_decision"], "filtered": state["filtered"], "wins": state["wins"], "losses": state["losses"], "win_rate": win_rate, "net_profit": round(state["net_profit"], 2), "starting_bankroll": STARTING_BANKROLL, "bankroll": round(state["bankroll"], 2), "growth_x": growth_x, "pending_count": len(state["pending"]), "recent_trades": state["trades"][:20], "equity_curve": equity_curve}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = "<html><body style='background:#0a0a0a;color:#eee;font-family:monospace;padding:20px'>"
    html = html + "<h2>CRSI + HTF TREND - LIVE STATS</h2><table id='t'></table>"
    html = html + "<h2>Equity Curve</h2><canvas id='c' width='600' height='200' style='background:#111;border:1px solid #222'></canvas>"
    html = html + "<h2>Recent Trades</h2><div id='tr'></div>"
    html = html + "<script>"
    html = html + "async function r(){const res=await fetch('/stats');const d=await res.json();"
    html = html + "const rows=[['Best Bid',d.best_bid],['Best Ask',d.best_ask],['CVD',d.cvd],['Last Signal',d.last_signal?d.last_signal.direction:'-'],['Last Decision',d.last_decision||'-'],['Filtered',d.filtered],['Pending',d.pending_count],['Wins',d.wins],['Losses',d.losses],['Win Rate',d.win_rate!==null?d.win_rate.toFixed(2)+'%':'n/a'],['Net Profit','$'+d.net_profit],['Starting Bankroll','$'+d.starting_bankroll],['Current Bankroll','$'+d.bankroll],['Growth',d.growth_x!==null?d.growth_x.toFixed(2)+'x':'n/a']];"
    html = html + "document.getElementById('t').innerHTML=rows.map(x=>'<tr><td style=\"color:#999;padding:4px\">'+x[0]+'</td><td style=\"color:#fff;padding:4px;text-align:right\">'+x[1]+'</td></tr>').join('');"
    html = html + "document.getElementById('tr').innerHTML=d.recent_trades.map(t=>'<div style=\"padding:3px 0\"><span style=\"color:'+(t.won?'#4caf50':'#f44336')+'\">'+(t.won?'WIN':'LOSS')+'</span> '+t.direction+' PnL $'+t.pnl+' Bankroll $'+t.bankroll_after+' '+t.time+'</div>').join('')||'No trades yet';"
    html = html + "const pts=d.equity_curve;const cv=document.getElementById('c');const ctx=cv.getContext('2d');ctx.clearRect(0,0,600,200);"
    html = html + "if(pts.length>1){const mn=Math.min(...pts,0);const mx=Math.max(...pts,0);const rg=(mx-mn)||1;ctx.beginPath();ctx.strokeStyle='#4dd0e1';ctx.lineWidth=2;pts.forEach((p,i)=>{const x=i*(600/(pts.length-1));const y=200-((p-mn)/rg)*180-10;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();}}"
    html = html + "r();setInterval(r,3000);"
    html = html + "</script></body></html>"
    return html
