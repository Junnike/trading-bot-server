import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import websockets
import requests
import os

app = FastAPI()

# ============ CONFIG (override via DO env vars if you want) ============
STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", "150"))
BET_PERCENT = float(os.getenv("BET_PERCENT", "2"))
MAX_BET_CAP = float(os.getenv("MAX_BET_CAP", "100"))
LIMIT_PRICE = float(os.getenv("LIMIT_PRICE", "0.5"))
RESOLVE_SECONDS = 15 * 60  # 15-min candle, matches the indicator

# ============ STATE ============
state = {
    "best_bid": None,
    "best_ask": None,
    "cvd": 0.0,
    "last_signal": None,
    "last_decision": None,
    "filtered": 0,
    "bankroll": STARTING_BANKROLL,
    "wins": 0,
    "losses": 0,
    "net_profit": 0.0,
    "trades": [],       # resolved trades, most recent first
    "pending": [],       # trades waiting to resolve
}

def mid_price():
    if state["best_bid"] is None or state["best_ask"] is None:
        return None
    return (state["best_bid"] + state["best_ask"]) / 2.0

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

# ============ TRADE RESOLUTION (bankroll compounding, same math as Pine) ============
async def resolve_trade(direction: str, entry_price: float, signal_time: float):
    pending_entry = {
        "direction": direction,
        "entry_price": entry_price,
        "signal_time": signal_time,
        "resolve_time": signal_time + RESOLVE_SECONDS,
    }
    state["pending"].append(pending_entry)

    await asyncio.sleep(RESOLVE_SECONDS)

    exit_price = mid_price()
    state["pending"] = [p for p in state["pending"] if p is not pending_entry]

    if exit_price is None:
        return

    won = (direction == "Up" and exit_price >= entry_price) or (direction == "Down" and exit_price < entry_price)

    bet_amount = min(state["bankroll"] *
