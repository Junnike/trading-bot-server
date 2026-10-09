import yfinance as yf, requests, zipfile, io, pandas as pd, time, sys
O='data/t9/'
for t in ['CL=F','BZ=F']:
    for i,p in [('1h','729d'),('15m','59d')]:
        for k in range(5):
            try:
                d=yf.download(t,period=p,interval=i,progress=False,auto_adjust=False)
                if len(d): break
            except Exception as e: print(e)
            time.sleep(2**(k+1))
        d.columns=[c[0] for c in d.columns]; d.index=d.index.tz_convert('UTC')
        d[['Close']].to_parquet(O+f'oil_{t[:2]}_{i}.parquet')
def get(url):
    for k in range(5):
        r=requests.get(url,timeout=60)
        if r.status_code==200: return r.content
        if r.status_code==404: return None
        time.sleep(2**(k+1))
for iv in ['1h','15m']:
    fr=[]
    # monthly Sep 2024.. Sep 2026, daily for current month
    for m in pd.period_range('2024-05','2026-10',freq='M'):
        c=get(f'https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/{iv}/BTCUSDT-{iv}-{m}.zip')
        if c is None:
            for d in pd.date_range(m.start_time,min(m.end_time,pd.Timestamp('2026-10-09'))):
                c2=get(f'https://data.binance.vision/data/spot/daily/klines/BTCUSDT/{iv}/BTCUSDT-{iv}-{d:%Y-%m-%d}.zip')
                if c2: fr.append(pd.read_csv(io.BytesIO(zipfile.ZipFile(io.BytesIO(c2)).read(zipfile.ZipFile(io.BytesIO(c2)).namelist()[0])),header=None))
        else:
            z=zipfile.ZipFile(io.BytesIO(c)); fr.append(pd.read_csv(z.open(z.namelist()[0]),header=None))
    b=pd.concat(fr).iloc[:,:6]; b.columns=['t','o','h','l','c','v']
    t=b.t.astype('int64'); b['t']=pd.to_datetime(t.where(t<1e14,t//1000),unit='ms',utc=True)
    b.drop_duplicates('t').sort_values('t').to_parquet(O+f'btc_{iv}.parquet'); print(iv,len(b),b.t.min(),b.t.max())
