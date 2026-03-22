import requests

r = requests.get('https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=3')
markets = r.json()

for m in markets:
    op = m.get('outcomePrices', [])
    print('raw:', op, type(op))
    if op:
        val = float(op[0])
        print('float:', val)
        print('passes filter:', 0.05 < val < 0.95)
    print()