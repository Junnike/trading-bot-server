# Stage 2: filter + stratified random sample -> data/t11_poly/sample.jsonl ; counts -> select_counts.json
import json, random, collections, sys
sys.path.insert(0, 'src')
from t11_poly_common import *
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 2500   # per category
MINVOL = 1000.0
cnt = collections.Counter(); seen = set(); pool = collections.defaultdict(list)
for l in open('data/t11_poly/markets.jsonl'):
    m = json.loads(l); cnt['raw_markets'] += 1
    if m['cid'] in seen: cnt['dup'] += 1; continue
    seen.add(m['cid'])
    if is_short_crypto(m['slug'], m['tags']): cnt['short_crypto_excluded'] += 1; continue
    if not (m['start'] and m['closed_t'] and m['tokens'] and m['prices']): cnt['missing_fields'] += 1; continue
    pr = json.loads(m['prices'])
    if sorted(pr) not in (['0', '1'], ['0.0', '1.0'], ['0', '1.0']) and not (len(pr) == 2 and sorted(float(x) for x in pr) == [0.0, 1.0]):
        cnt['unresolved_or_5050_voided'] += 1; continue
    if len(json.loads(m['outcomes'])) != 2: cnt['not_binary'] += 1; continue
    if json.loads(m['outcomes']) != ['Yes', 'No']: cnt['nonyesno_binary_included(outcome0 token)'] += 1
    if (m['vol'] or 0) < MINVOL: cnt['below_minvol'] += 1; continue
    s, c = ts(m['start']), ts(m['closed_t'])
    if c - s < 3600: cnt['life_lt_1h'] += 1; continue
    cat = category(m['tags'])
    yes = 1 if float(pr[0]) == 1.0 else 0
    pool[cat].append(dict(cid=m['cid'], slug=m['slug'], cat=cat, tok=json.loads(m['tokens'])[0], start=s, close=c, yes=yes, vol=m['vol'], fee=(m['fs'] or {}).get('rate') if m['fees'] else 0.0, tags=m['tags']))
random.seed(11)
out = []
for cat, L in pool.items():
    cnt['eligible_' + cat] = len(L)
    random.shuffle(L); out += L[:CAP]; cnt['sampled_' + cat] = min(CAP, len(L))
random.shuffle(out)
with open('data/t11_poly/sample.jsonl', 'w') as f:
    for x in out: f.write(json.dumps(x) + '\n')
json.dump(cnt, open('data/t11_poly/select_counts.json', 'w'), indent=1); print(dict(cnt))
