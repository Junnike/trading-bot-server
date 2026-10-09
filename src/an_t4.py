import json,sys,numpy as np
rows=[json.loads(l) for l in open("data/t4_poll.jsonl")]
ok=[r for r in rows if r["ok"]]
def analyze():
    if not ok: return None
    hrs=(ok[-1]["ts"]-ok[0]["ts"])/3600
    nets=np.array([r["best"]["net"] for r in ok if r.get("best")])
    gross=np.array([r["best"]["gross"] for r in ok if r.get("best")])
    pos=[r for r in ok if r.get("best") and r["best"]["net"]>0]
    big=[r for r in ok if r.get("best") and r["best"]["net"]>=0.01]
    # duration of consecutive snapshots with net>0
    runs=[];cur=0
    for r in ok:
        if r.get("best") and r["best"]["net"]>0: cur+=1
        else:
            if cur: runs.append(cur)
            cur=0
    if cur: runs.append(cur)
    return dict(snaps=len(ok),fail=len(rows)-len(ok),hours=hrs,max_net=float(nets.max()) if len(nets) else None,max_gross=float(gross.max()) if len(gross) else None,
        n_pos=len(pos),n_ge1c=len(big),runs_min=runs,
        pos_detail=[(r["best"]["A"],r["best"]["B"],round(r["best"]["net"],4),r["best"]["szA"],r["best"]["szB"],bool(r.get("ob"))) for r in pos[:5]],
        pairs_mean=float(np.mean([r["npairs"] for r in ok])))
if __name__=="__main__": print(analyze())
