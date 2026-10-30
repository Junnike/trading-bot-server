import urllib.request, urllib.parse, re, json, sys, time
OUT=sys.argv[1]
def get(u,data=None):
    for w in (0,2,4,8,16):
        time.sleep(w)
        try:
            req=urllib.request.Request(u,data=data,headers={'User-Agent':'curl/8.0','Content-Type':'application/json'})
            return urllib.request.urlopen(req,timeout=60).read()
        except Exception as e: err=e
    raise err
syms=[];marker=''
while True:
    u='https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/daily/klines/'+('&marker='+urllib.parse.quote(marker) if marker else '')
    x=get(u).decode()
    syms+=re.findall(r'<Prefix>data/futures/um/daily/klines/([^/]+)/</Prefix>',x)
    if '<IsTruncated>true' in x:
        marker=re.search(r'<NextMarker>([^<]+)',x).group(1)
    else: break
json.dump(sorted(set(syms)),open(OUT+'/um_symbols.json','w'))
print(len(syms))
d=json.loads(get('https://api.hyperliquid.xyz/info',json.dumps({"type":"meta","dex":"xyz"}).encode()))
json.dump([u['name'] for u in d['universe']],open(OUT+'/hl_xyz.json','w'))
print([u['name'] for u in d['universe']])
