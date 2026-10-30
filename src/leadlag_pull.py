# Downloads Binance USD-M 1m klines (public) -> parquet per symbol in data/leadlag/k1m/. Untrusted zips parsed in-memory only.
import urllib.request, zipfile, io, sys, time, datetime as dt, os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
OUT='/home/user/trading-bot-server/data/leadlag/k1m'; os.makedirs(OUT,exist_ok=True)
START=dt.date(2026,4,28); END=dt.date(2026,10,27)
TRAD=['TSLAUSDT','NVDAUSDT','XAUUSDT','XAGUSDT','CLUSDT','BZUSDT','SPYUSDT','QQQUSDT','XAUTUSDT','AAPLUSDT','AMZNUSDT','COINUSDT','MSTRUSDT','METAUSDT','GOOGLUSDT','MSFTUSDT','HOODUSDT','CRCLUSDT','PLTRUSDT','INTCUSDT','XPTUSDT','XPDUSDT','NATGASUSDT','EWYUSDT']
CRY=['BTC','ETH','SOL','BNB','XRP','DOGE','ADA','AVAX','LINK','TRX','DOT','LTC','BCH','NEAR','SUI','APT','ARB','OP','ATOM','UNI','AAVE','FIL','ETC','INJ','TON','HBAR','ICP','TAO','WLD','ENA','PEPE','SHIB','XLM','ALGO','SEI','TIA','ONDO','RENDER','FET','JUP','LDO','CRV','MKR','STX','IMX','GALA','PENDLE','WIF','BONK','ZEC']
CRY=[c+'USDT' for c in CRY]
def fetch(u):
    for w in (0,2,4,8,16):
        time.sleep(w)
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8.0'}),timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code==404: return None
        except Exception: pass
    return 'ERR'
def parse(b):
    z=zipfile.ZipFile(io.BytesIO(b)); df=pd.read_csv(z.open(z.namelist()[0]),header=None if True else 0)
    if not str(df.iloc[0,0]).isdigit(): df=df.iloc[1:]
    df=df.iloc[:,[0,1,2,3,4,5,7]].astype(float); df.columns=['t','o','h','l','c','v','qv']; return df
def urls(s):
    base='https://data.binance.vision/data/futures/um/'
    d=START; L=[]
    months={}
    while d<=END:
        months.setdefault((d.year,d.month),[]).append(d); d+=dt.timedelta(1)
    for (y,m),days in months.items():
        import calendar
        full=len(days)==calendar.monthrange(y,m)[1]
        if full: L.append(base+f'monthly/klines/{s}/1m/{s}-1m-{y}-{m:02d}.zip')
        else: L+= [base+f'daily/klines/{s}/1m/{s}-1m-{x}.zip' for x in days]
    return L
def do(s):
    f=f'{OUT}/{s}.parquet'
    if os.path.exists(f): return s,'cached'
    parts=[];miss=0
    for u in urls(s):
        b=fetch(u)
        if b is None: miss+=1; continue
        if b=='ERR': miss+=1000; continue
        parts.append(parse(b))
    if not parts: return s,'none'
    df=pd.concat(parts).drop_duplicates('t').sort_values('t'); df['t']=df['t'].astype('int64')
    df.to_parquet(f); return s,f'{len(df)} rows miss={miss}'
if __name__=='__main__':
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(do,TRAD+CRY): print(*r,flush=True)
