"""Classify raw market lists (data/tradfi/raw_*.json from tradfi_fetch.py) -> data/tradfi/markets_all.parquet/json + summary_by_venue.json."""
import json, re, collections, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tradfi_classify import norm, category, COMMODITY, INDEX, ETF, PREIPO, FX_RE
import pandas as pd
D = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
L = lambda k: json.load(open(D / f"raw_{k}.json"))
rows = []
def add(venue, sym, base, cat, maker=None, taker=None, lev=None, hours=None, status=None, tag=None):
    if cat in (None, "crypto", "token_gold"): return
    rows.append(dict(venue=venue, symbol=sym, base=base, cat=cat, maker=maker, taker=taker, max_lev=lev, hours=hours, status=status, tag=tag))
def fl(x):
    try: return float(x)
    except Exception: return None
# ---------- tagged venues ----------
def tagged(venue, items, getsym, is_tf, **kw):
    for it in items:
        s = getsym(it)
        if not is_tf(it): continue
        b = norm(s); c = category(b, True)
        add(venue, s, b, c, **{k: f(it) for k, f in kw.items()})
# Aster
a = [x for x in L("aster")["symbols"] if x["status"] == "TRADING" and set(x.get("underlyingSubType", [])) & {"STOCK", "ETF", "Commodities"}]
tagged("Aster", a, lambda x: x["symbol"], lambda x: True, tag=lambda x: ",".join(x["underlyingSubType"]), status=lambda x: x["status"])
# OKX
tagged("OKX", [x for x in L("okx")["data"] if x["state"] == "live" and x["instCategory"] in ("3", "4")], lambda x: x["instId"], lambda x: True,
       lev=lambda x: fl(x["lever"]), tag=lambda x: "cat" + x["instCategory"])
# Bitget (isRwa)
tagged("Bitget", [x for x in L("bitget")["data"] if x["isRwa"] == "YES" and x["symbolStatus"] == "normal"], lambda x: x["symbol"], lambda x: True,
       maker=lambda x: fl(x["makerFeeRate"]), taker=lambda x: fl(x["takerFeeRate"]), lev=lambda x: fl(x["maxLever"]), tag=lambda x: "isRwa")
# MEXC
TF_PLATES = {"mc-trade-zone-tradfi", "mc-trade-zone-Stock", "mc-trade-zone-usstocks", "mc-trade-zone-stockindex", "mc-trade-zone-ETF", "mc-trade-zone-jpstocks",
             "mc-trade-zone-twstocks", "mc-trade-zone-hkstocks", "mc-trade-zone-Commodities", "mc-trade-zone-metalsfutures", "mc-trade-zone-metals", "mc-trade-zone-Forex",
             "mc-trade-zone-OIL", "mc-trade-zone-preipo", "mc-trade-zone-privity"}
tagged("MEXC", [x for x in L("mexc")["data"] if x["state"] == 0 and set(x["conceptPlate"]) & TF_PLATES], lambda x: x["symbol"], lambda x: True,
       maker=lambda x: x["makerFeeRate"], taker=lambda x: x["takerFeeRate"], lev=lambda x: x["maxLeverage"], tag=lambda x: "zero" if x.get("isZeroFeeSymbol") else "")
# HTX
tagged("HTX", [x for x in L("htx")["data"] if x["contract_status"] == 1 and x["tradfi_labels"]], lambda x: x["contract_code"], lambda x: True, tag=lambda x: ",".join(x["tradfi_labels"]))
# Crypto.com
CCPT = {"EQUITY", "EQUITY_IND", "COMMODITIES", "PRE_IPO"}
tagged("Crypto.com", [x for x in L("cryptocom")["result"]["data"] if x["inst_type"] == "PERPETUAL_SWAP" and x["product_type"] in CCPT and x["tradable"]],
       lambda x: x["symbol"], lambda x: True, lev=lambda x: fl(x["max_leverage"]), tag=lambda x: x["product_type"])
# Deepcoin
tagged("Deepcoin", [x for x in L("deepcoin")["data"] if x["assetType"] != "crypto" and x["state"] == "live"], lambda x: x["instId"], lambda x: True, lev=lambda x: fl(x["lever"]), tag=lambda x: x["assetType"])
# Extended
for x in L("extended")["data"]:
    if x["category"] != "RWA" or not x["active"]: continue
    s = x["name"]; b = norm(s); b = re.sub(r"_24_5$", "", b)
    c = category(b, True)
    if x["subCategory"] == "Pre-market": c = "preipo"
    add("Extended", s, b, c, maker=0.0, taker=0.00010, lev=fl(x["tradingConfig"]["maxLeverage"]), hours=x["tradingHours"], tag=x["subCategory"])
# Backpack
for x in L("backpack"):
    if x["marketType"] != "PERP" or not x["rwaMarketType"]: continue
    s = x["symbol"]; b = norm(s); c = category(b, True) if b in ETF or b == "DRAM" else ("indices" if x["rwaMarketType"] == "INDEX" else category(b, True))
    add("Backpack", s, b, c, tag=x["rwaMarketType"])
# BingX
for x in L("bingx")["data"]:
    s = x["symbol"]
    if not s.startswith("NC") or x["status"] != 1: continue
    pre, rest = s[:4], s[4:].split("-")[0]
    rest = re.sub(r"2USD$|USD$", "", rest)
    rest = re.sub(r"^\d{0,3}(?=OIL|NATGAS|COPPER)", "", rest) if pre == "NCCO" else rest
    rest = re.sub(r"^(7241|724)", "", rest)
    rest = re.sub(r"2$", "", rest) if pre in ("NCSK", "NCSI") and not rest.endswith("TSM2") else rest
    if pre == "NCFX": c = "fx"
    elif pre == "NCCO": c = "commodities"
    elif pre == "NCSI": c = "etf" if rest in ETF else ("indices")
    else: c = category(rest, True)
    add("BingX", s, rest, c, maker=x["makerFeeRate"], taker=x["takerFeeRate"], tag=pre)
# Phemex TradFi
for x in L("phemex")["data"]["perpProductsV2"]:
    if x.get("perpProductSubType") not in ("TradFi",) or x["status"] != "Listed": continue
    s = x["symbol"]; b = norm(s); add("Phemex", s, b, category(b, True), lev=x["maxLeverage"], tag="TradFi")
# ---------- universe for untagged venues ----------
cnt = collections.defaultdict(set)
for r in rows:
    if r["cat"] == "stocks": cnt[r["base"]].add(r["venue"])
UNIVERSE = {b for b, v in cnt.items() if len(v) >= 3} - {"PURR", "PENG", "PEP", "ARC", "BIO", "CHIP", "NET", "LIN", "ON", "DE", "MP", "BA", "BE", "BB", "V", "GE", "CAT", "WEN", "RAM", "BOT", "CC", "MET", "AI", "LIT", "HD", "NU", "ADI", "NOW", "QNT", "DATA", "MOON", "FLEX", "OPEN", "PL", "ZM", "XP", "NOK", "S", "TEM", "TER", "TWST", "ONDS", "ASTS", "CIEN", "LITE", "GLW"} | {"NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "MSTR", "COIN", "HOOD", "PLTR", "AMD", "INTC", "MU", "AVGO", "ORCL", "NFLX", "CRCL", "BABA", "TSM", "ASML", "ARM", "SNDK", "BMNR", "RKLB", "DELL", "IBM", "WDC", "QCOM", "MRVL", "SMCI", "COST", "LLY", "UNH", "NBIS", "CRWV", "IREN", "TTWO", "AAOI", "SAMSUNG", "SKHYNIX", "SKHY", "HYUNDAI", "TENCENT", "XIAOMI", "MINIMAX", "ZHIPU", "KIOXIA", "CBRS", "STRC", "GME", "DRAM", "MRNA", "GEV", "USAR", "DKNG", "RDDT", "CRWD"}
UNIVERSE -= {"DASH", "STX", "CVX", "EQT", "MAR", "ROK", "HUT", "COP", "RUM"}
json.dump(sorted(UNIVERSE), open(D / "stock_universe_matched.json", "w"))
def match(venue, items, getsym, **kw):
    for it in items:
        s = getsym(it); b = norm(s); b = re.sub(r"^(1000)(?=[A-Z]{3,})", "", b)
        c = category(b, False)
        if c is None and b in UNIVERSE: c = "stocks"
        if c is None and b in ("TSLAX","NVDAX","MSTRX","HOODX","GOOGLX","CRCLX","AAPLX","AMZNX","COINX","METAX","SPCXX","OURAX","MOONSHOTX","ANTHROPICX","OPENAIX","GLDX","QQQX","SPYX","SOFIX"): c = "x"
        if c == "x":
            b = b[:-1]; c = {"GLDX": "etf", "QQQX": "etf", "SPYX": "etf"}.get(b + "X") or category(b, True)
            if b == "GLD": b = "GLD"
        if c is None: continue
        add(venue, s, b, c, **{k: f(it) for k, f in kw.items()})
match("Gate", [x for x in L("gate") if not x["in_delisting"]], lambda x: x["name"], maker=lambda x: fl(x["maker_fee_rate"]), taker=lambda x: fl(x["taker_fee_rate"]), lev=lambda x: fl(x["leverage_max"]))
match("KuCoin", [x for x in L("kucoin")["data"] if x["status"] == "Open" and x["type"] == "FFWCSX"], lambda x: x["baseCurrency"], maker=lambda x: x["makerFeeRate"], taker=lambda x: x["takerFeeRate"], lev=lambda x: x.get("maxLeverage"))
match("Bitunix", [x for x in L("bitunix")["data"] if x["symbolStatus"] == "OPEN"], lambda x: x["symbol"], lev=lambda x: x["maxLeverage"])
match("WOO X", [x for x in L("woox")["rows"] if x["symbol"].startswith("PERP_") and x["status"] == "TRADING"], lambda x: x["symbol"].split("_")[1])
match("Kraken", [x for x in L("kraken")["instruments"] if x["symbol"].startswith("PF_") and x["tradeable"]], lambda x: x["symbol"])
match("Lighter", [x for x in L("lighter")["order_book_details"] if x["status"] == "active" and x["market_type"] == "perp"], lambda x: x["symbol"], maker=lambda x: fl(x["maker_fee"]), taker=lambda x: fl(x["taker_fee"]))
# Phemex non-tagged (also old products list)
# ---------- Hyperliquid ----------
for dex, m in L("hl_meta").items():
    for u in m["universe"]:
        if u.get("isDelisted"): continue
        s = u["name"]; b = norm(s)
        if dex in ("", "hyna"):
            c = category(b, False)
            if c is None or b in ("SPX", "PURR", "GAS"): continue
        else:
            c = "other" if b in ("TOTAL2", "OTHERS", "BTCD") and False else category(b, True)
            if b in ("TOTAL2", "OTHERS", "BTCD", "BTC", "ETH", "XMR", "USDE", "ANSEM", "PURRDAT", "BIRD", "TREAD", "PAPER", "CAR", "ANT", "PRL", "SBE", "TCNT", "PURR", "BVIV") and b not in ("PURRDAT",): c = None
        add("Hyperliquid HIP-3", s, b, c, lev=u["maxLeverage"], tag=dex)
# ---------- oracle DEXs ----------
og = L("gains"); gr = {i: g["name"] for i, g in enumerate(og["groups"])}
for p in og["pairs"]:
    g = gr[int(p["groupIndex"])]
    if g in ("crypto", "altcoins", "crypto-degen"): continue
    s = p["from"] + "/" + p["to"]; b = p["from"]
    c = {"forex": "fx", "forex-minor": "fx", "forex-exotic": "fx", "commodities-1": "commodities", "commodities-2": "commodities", "indices": "indices"}.get(g) or "stocks"
    if c == "fx": b = p["from"] + p["to"]
    if b in ETF and c == "stocks": c = "etf"
    add("Gains gTrade", s, b, c, tag=g)
av = L("avantis")["data"]["pairInfos"]
for k, p in av.items():
    gi = p["groupIndex"]
    if gi not in (2, 3, 6) or p["from"] in ("", "DELISTED"): continue
    s = p["from"] + "/" + p["to"]; b = p["from"]
    c = {2: "fx", 3: "commodities", 6: "stocks"}[gi]
    if c == "fx": b = p["from"] + p["to"]
    if gi == 6:
        c = category(b, True)
    add("Avantis", s, b, c, lev=p["leverages"]["maxLeverage"], tag="g%d" % gi, maker=p.get("openFeeP"))
CRYPTO_OST = {"BTC", "ETH", "SOL", "XRP", "BNB", "HYPE", "ADA", "LINK", "TRX"}
for p in L("ostium"):
    f, t = p["from"], p["to"]
    if f in CRYPTO_OST: continue
    if t != "USD" or f in ("EUR", "GBP", "AUD", "NZD", "USD"):
        c = "fx" if (f in ("EUR", "GBP", "AUD", "NZD", "USD")) else "indices"
        b = f + t
    else:
        b = f; c = category(b, True)
        if b in ("BRENT", "CL", "HG", "XAU", "XAG", "XPT", "XPD", "COCOA", "COFFEE", "COTTON", "SUGAR", "DIESEL", "UNG"): c = "commodities" if b != "UNG" else "etf"
        if b in ("SPX", "NDX", "DJI"): c = "indices"
        if b in ("HYG", "URA", "REMX", "TLT", "XLE", "UNG"): c = "etf"
    add("Ostium", f + "/" + t, b, c, hours="follows underlying (feed isMarketOpen)")
df = pd.DataFrame(rows).drop_duplicates(["venue", "symbol"])
df.to_json(D / "markets_all.json", orient="records", indent=0)
df.to_parquet(D / "markets_all.parquet")
pv = df.pivot_table(index="venue", columns="cat", values="symbol", aggfunc="count", fill_value=0)
pv["TOTAL"] = pv.sum(axis=1)
pv = pv.sort_values("TOTAL", ascending=False)
pv.to_csv(D / "summary_by_venue.csv")
print(pv.to_string())
