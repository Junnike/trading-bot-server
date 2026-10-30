"""Fetch raw public market lists of venues (no keys) into data/tradfi/raw_<venue>.json."""
import json, subprocess, sys, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
OUT.mkdir(parents=True, exist_ok=True)
GET = {
 "aster": "https://fapi.asterdex.com/fapi/v1/exchangeInfo",
 "okx": "https://www.okx.com/api/v5/public/instruments?instType=SWAP",
 "bitget": "https://api.bitget.com/api/v2/mix/market/contracts?productType=USDT-FUTURES",
 "gate": "https://api.gateio.ws/api/v4/futures/usdt/contracts",
 "mexc": "https://contract.mexc.com/api/v1/contract/detail",
 "bingx": "https://open-api.bingx.com/openApi/swap/v2/quote/contracts",
 "phemex": "https://api.phemex.com/public/products",
 "lighter": "https://mainnet.zklighter.elliot.ai/api/v1/orderBookDetails",
 "extended": "https://api.starknet.extended.exchange/api/v1/info/markets",
 "edgex": "https://pro.edgex.exchange/api/v1/public/meta/getMetaData",
 "backpack": "https://api.backpack.exchange/api/v1/markets",
 "kraken": "https://futures.kraken.com/derivatives/api/v3/instruments",
 "ostium": "https://metadata-backend.ostium.io/PricePublish/latest-prices",
 "cryptocom": "https://api.crypto.com/exchange/v1/public/get-instruments",
 "htx": "https://api.hbdm.com/linear-swap-api/v1/swap_contract_info",
 "kucoin": "https://api-futures.kucoin.com/api/v1/contracts/active",
 "bitunix": "https://fapi.bitunix.com/api/v1/futures/market/trading_pairs",
 "woox": "https://api.woo.org/v1/public/info",
 "deepcoin": "https://api.deepcoin.com/deepcoin/market/instruments?instType=SWAP",
}
POST = {"hl_perpdexs": {"type": "perpDexs"}}
def curl(url, data=None):
    c = ["curl","-s","-m","30",url]
    if data: c += ["-X","POST","-H","content-type: application/json","-d",json.dumps(data)]
    return subprocess.run(c,capture_output=True,text=True).stdout
if __name__ == "__main__":
    only = sys.argv[1:]
    for k,u in GET.items():
        if only and k not in only: continue
        (OUT/f"raw_{k}.json").write_text(curl(u)); print(k)
    for k,d in POST.items():
        (OUT/f"raw_{k}.json").write_text(curl("https://api.hyperliquid.xyz/info",d)); print(k)
    # HL meta per dex
    dexs = json.loads((OUT/"raw_hl_perpdexs.json").read_text())
    allm = {}
    for d in dexs:
        if d is None: name=""
        else: name=d["name"]
        allm[name]=json.loads(curl("https://api.hyperliquid.xyz/info",{"type":"meta","dex":name}))
    (OUT/"raw_hl_meta.json").write_text(json.dumps(allm))
