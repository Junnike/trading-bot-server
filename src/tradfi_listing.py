"""Listing dates of the non-crypto markets per venue (from instrument metadata) -> data/tradfi/listing_dates.json"""
import json, pathlib, datetime, statistics
import pandas as pd
D = pathlib.Path(__file__).resolve().parent.parent / "data" / "tradfi"
L = lambda k: json.load(open(D / f"raw_{k}.json"))
df = pd.read_parquet(D / "markets_all.parquet")
M = {}
for x in L("aster")["symbols"]: M[("Aster", x["symbol"])] = x["onboardDate"]
for x in L("okx")["data"]: M[("OKX", x["instId"])] = int(x["listTime"])
for x in L("gate"): M[("Gate", x["name"])] = x["create_time"] * 1000
for x in L("mexc")["data"]: M[("MEXC", x["symbol"])] = x["createTime"]
for x in L("bingx")["data"]: M[("BingX", x["symbol"])] = x["launchTime"]
for x in L("htx")["data"]: M[("HTX", x["contract_code"])] = int(datetime.datetime.strptime(x["create_date"], "%Y%m%d").timestamp() * 1000)
for x in L("kucoin")["data"]: M[("KuCoin", x["baseCurrency"])] = x["firstOpenDate"]
for x in L("bitunix")["data"]: M[("Bitunix", x["symbol"])] = int(x["launchTime"])
for x in L("lighter")["order_book_details"]: M[("Lighter", x["symbol"])] = int(x["created_at"])
for x in L("phemex")["data"]["perpProductsV2"]: M[("Phemex", x["symbol"])] = x["listTime"]
for x in L("kraken")["instruments"]: M[("Kraken", x["symbol"])] = int(datetime.datetime.fromisoformat(x["openingDate"].replace("Z", "+00:00")).timestamp() * 1000) if x.get("openingDate") else 0
for x in L("backpack"): M[("Backpack", x["symbol"])] = int(datetime.datetime.fromisoformat(x["createdAt"]).replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
out = {}
for v, g in df.groupby("venue"):
    t = [M[(v, s)] for s in g.symbol if (v, s) in M and M[(v, s)] > 1e12]
    if not t: continue
    f = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.UTC).strftime("%Y-%m-%d")
    out[v] = dict(n=len(t), first=f(min(t)), median=f(statistics.median(t)), last=f(max(t)))
json.dump(out, open(D / "listing_dates.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
