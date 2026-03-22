import requests
import json

def get_markets():
    print("Connecting to Polymarket...")

    url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50"
    response = requests.get(url, timeout=10)
    all_markets = response.json()
    print(f"Downloaded {len(all_markets)} active markets")

    good_markets = []

    for market in all_markets:
        try:
            # outcomePrices comes as a STRING like '["0.2055", "0.7945"]'
            # so we need json.loads to convert it to a real list first
            raw = market.get("outcomePrices", "[]")
            outcome_prices = json.loads(raw)

            if not outcome_prices:
                continue

            yes_price = float(outcome_prices[0])

            if 0.05 < yes_price < 0.95:
                raw_ids = market.get("clobTokenIds", "[]")
                clob_ids = json.loads(raw_ids) if isinstance(raw_ids, str) else raw_ids

                good_markets.append({
                    "question":    market.get("question", "Unknown"),
                    "market_prob": yes_price,
                    "yes_token":   clob_ids[0] if len(clob_ids) > 0 else "",
                    "no_token":    clob_ids[1] if len(clob_ids) > 1 else "",
                })

        except Exception:
            continue

    print(f"Found {len(good_markets)} good markets!")
    return good_markets


if __name__ == "__main__":
    markets = get_markets()
    print()
    for m in markets[:5]:
        print(f"  {m['market_prob']:.0%} YES | {m['question']}")