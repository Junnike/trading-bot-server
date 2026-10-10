import json, datetime as dt
def ts(s):
    s = s.replace(' ', 'T')
    if s.endswith('Z'): s = s[:-1] + '+00:00'
    elif s.endswith('+00'): s += ':00'
    return int(dt.datetime.fromisoformat(s).timestamp())
CATS = [  # first match wins; labels from gamma event tags
 ('Weather', ['Weather', 'Temperature', 'Climate & Science', 'Hurricanes', 'Daily Temperature']),
 ('Sports', ['Sports', 'NBA', 'NFL', 'MLB', 'NHL', 'Soccer', 'Football', 'Tennis', 'UFC', 'MMA', 'Esports', 'Games', 'Cricket', 'F1', 'Golf', 'Basketball', 'Baseball', 'Hockey', 'Boxing', 'College Football', 'NCAA', 'EPL', 'Champions League', 'La Liga']),
 ('Politics', ['Politics', 'Elections', 'Global Elections', 'US Politics', 'Trump', 'World', 'Geopolitics', 'Government', 'Congress', 'Middle East', 'Ukraine', 'Mention Markets', 'Trump Mentions']),
 ('EconData', ['Economy', 'Economic Policy', 'Fed', 'Fed Rates', 'Inflation', 'CPI', 'Jobs', 'GDP', 'Interest Rates', 'Jerome Powell', 'Fed Chair']),
 ('Finance', ['Finance', 'Stocks', 'Equities', 'Commodities', 'Indices', 'Earnings', 'Business', 'Tech', 'Big Tech', 'Companies', 'IPOs', 'Oil', 'Gold']),
 ('Crypto', ['Crypto', 'Crypto Prices', 'Bitcoin', 'Ethereum', 'Solana', 'Token Sales', 'Airdrops', 'DeFi']),
 ('Culture', ['Culture', 'Pop Culture', 'Movies', 'Music', 'Awards', 'Oscars', 'Celebrities', 'TV', 'Social Media', 'Twitter', 'Elon Musk', 'Entertainment', 'AI']),
]
def category(tags):
    s = set(tags)
    for name, keys in CATS:
        if s & set(keys): return name
    return 'Other'
def is_short_crypto(slug, tags):
    return any(k in (slug or '') for k in ('-updown-5m-', '-updown-15m-', '-up-or-down-')) or '5M' in tags or '15M' in tags
