import json,sys; sys.path.insert(0,'src')
from kcommon import get
out=[];cur=None
while True:
    p={"limit":200}
    if cur:p["cursor"]=cur
    d=get("/series",p)
    if not d: print("FAIL");break
    out+=d["series"];cur=d.get("cursor")
    if not cur:break
k=[s for s in out if s["ticker"].endswith("15M")]
json.dump(k,open("data/series.json","w"))
print(len(out),[ (s["ticker"],s.get("fee_type"),s.get("fee_multiplier")) for s in k])
