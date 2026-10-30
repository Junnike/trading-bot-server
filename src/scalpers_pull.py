"""Pull public portfolio + up to 10k latest fills per candidate wallet (resumable cache in data/scalpers/raw/)."""
import json, gzip, os, time, subprocess, sys
D='data/scalpers/'; os.makedirs(D+'raw',exist_ok=True)
URL='https://api.hyperliquid.xyz/info'
def post(body):
    for wait in (0,2,4,8,16,32):
        time.sleep(wait)
        p=subprocess.run(['curl','-sS','-m','60','-X','POST','-H','Content-Type: application/json','-d',json.dumps(body),URL,'-w','\n%{http_code}'],capture_output=True,text=True)
        out,_,code=p.stdout.rpartition('\n')
        if code=='200':
            time.sleep(1.0); return json.loads(out)
        if code=='429': time.sleep(10)
    return None
cands=json.load(open(D+'candidates.json'))
for i,c in enumerate(cands):
    f=D+'raw/'+c['addr']+'.json.gz'
    if os.path.exists(f): continue
    a=c['addr']; port=post({'type':'portfolio','user':a})
    fills=[]; st=int((time.time()-45*86400)*1000)
    for page in range(15):
        r=post({'type':'userFillsByTime','user':a,'startTime':st,'aggregateByTime':False})
        if not r: break
        fills+=r
        if len(r)<2000: break
        st=max(x['time'] for x in r)+1
    seen=set(); u=[]
    for x in fills:
        k=(x['tid'],x['oid'],x['time'])
        if k not in seen: seen.add(k); u.append(x)
    with gzip.open(f,'wt') as g: json.dump({'addr':a,'portfolio':port,'fills':u},g)
    print(i,a,len(u),flush=True)
