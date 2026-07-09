import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import websockets
import requests
import os

app = FastAPI()

# ============ STATE ============
state = {
    "best_bid": None,
    "best_ask": None,
    "cvd": 0.0,
    "last_signal": None,
    "last_decision": None,
    "trades": [],
    "wins": 0,
    "losses": 0,
    "filtered": 0,
}

# ============ BINANCE WEBSOCKET (orderbook + trades) ============
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

# ============ DECISION GATE ============
def orderbook_confirms(direction: str) -> bool:
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

# ============ WEBHOOK FROM TRADINGVIEW ============
@app.post("/tv-signal")
async def tv_signal(request: Request):
    payload = await request.json()
    direction = payload.get("direction")
    state["last_signal"] = {"direction": direction, "time": time.time()}

    if orderbook_confirms(direction):
        decision = "TRADE"
    else:
        decision = "FILTERED"
        state["filtered"] += 1

    state["last_decision"] = decision
    state["trades"].append({
        "direction": direction,
        "decision": decision,
        "cvd_at_signal": state["cvd"],
        "time": time.time()
    })

    notify_telegram(f"Signal: {direction} | Decision: {decision} | CVD: {state['cvd']:.1f}")
    return {"status": "ok", "decision": decision}

# ============ TELEGRAM NOTIFIER ============
def notify_telegram(text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# ============ DASHBOARD ============
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return f"""
    <html><body style="background:#111;color:#eee;font-family:monospace;padding:20px">
    <h2>Trading Bot Live Stats</h2>
    <p>Best Bid: {state['best_bid']}</p>
    <p>Best Ask: {state['best_ask']}</p>
    <p>CVD: {state['cvd']:.1f}</p>
    <p>Last Signal: {state['last_signal']}</p>
    <p>Last Decision: {state['last_decision']}</p>
    <p>Filtered: {state['filtered']}</p>
    <p>Total Signals: {len(state['trades'])}</p>
    </body></html>
    """
