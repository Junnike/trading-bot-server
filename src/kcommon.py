import json, time, threading, requests, fcntl, os, struct
BASE="https://api.elections.kalshi.com/trade-api/v2"
H={"User-Agent":"curl/8.0","Accept":"application/json"}
GAP=0.15  # kept for compat; global cross-process limiter below enforces ~6.7 req/s total
SLOT=0.2
_lock=threading.Lock()
_LF="/home/user/trading-bot-server/data/.ratelimit"
def _pause(sec):
    with _lock:
        fd=os.open(_LF,os.O_RDWR|os.O_CREAT)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX)
            raw=os.read(fd,8); nxt=struct.unpack("d",raw)[0] if len(raw)==8 else 0.0
            os.lseek(fd,0,0); os.write(fd,struct.pack("d",max(nxt,time.time()+sec)))
        finally: os.close(fd)
def _slot():
    with _lock:
        fd=os.open(_LF,os.O_RDWR|os.O_CREAT)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX)
            raw=os.read(fd,8)
            nxt=struct.unpack("d",raw)[0] if len(raw)==8 else 0.0
            now=time.time(); t=max(now,nxt)
            try: sl=float(open('/home/user/trading-bot-server/data/.slot').read())
            except Exception: sl=SLOT
            os.lseek(fd,0,0); os.write(fd,struct.pack("d",t+sl))
        finally:
            os.close(fd)
    if t>now: time.sleep(t-now)
_SF='/home/user/trading-bot-server/data/.slot'
_ok=[0]
def _adj(f,lo=0.13,hi=1.5):
    try: v=float(open(_SF).read())
    except Exception: v=SLOT
    v=min(hi,max(lo,v*f)); open(_SF,'w').write(str(v))
def get(path, params=None, session=None):
    s=session or requests
    for wait in (0,2,4,8,16):
        if wait: time.sleep(wait)
        _slot()
        try:
            r=s.get(BASE+path,params=params,headers=H,timeout=30)
        except Exception as e:
            continue
        if r.status_code==429:
            open('/home/user/trading-bot-server/data/429.log','a').write(f'{time.time()} {path}\n'); time.sleep(10); continue
        open('/home/user/trading-bot-server/data/req.log','a').write(f'{time.time():.1f} {r.status_code}\n')
        if r.status_code==200:
            _ok[0]+=1
            try: return r.json()
            except Exception: continue
        if r.status_code in (400,404): return {"_err":r.status_code,"_body":r.text[:200]}
    return None
