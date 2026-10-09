import json,sys,os; sys.path.insert(0,'src')
from kcommon import get
for S in sys.argv[1:]:
    fn=f"data/markets_{S}.jsonl"
    if os.path.exists(fn+".done"): continue
    seen={};ok=True
    for ep,extra in (("/markets",{"status":"settled"}),("/historical/markets",{})):
        cur=None
        while True:
            p={"series_ticker":S,"limit":1000,**extra}
            if cur:p["cursor"]=cur
            d=get(ep,p)
            if not d or "markets" not in d: print("FAIL",S,ep,flush=True);ok=False;break
            for m in d["markets"]:
                if m.get("result") in ("yes","no"): seen[m["ticker"]]=m
            cur=d.get("cursor")
            if not cur:break
    if ok:
        with open(fn,"w") as f:
            for m in sorted(seen.values(),key=lambda m:m["open_time"]): f.write(json.dumps(m)+"\n")
        open(fn+".done","w").write(str(len(seen)))
    print(S,len(seen),flush=True)
