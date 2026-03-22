from get_markets import get_markets
from get_news    import get_news
from ask_ai      import ask_ai

MINIMUM_EDGE = 0.08

def find_signals(max_markets=25):
    print("\n[1/3] Fetching markets...")
    markets = get_markets()
    markets_to_check = markets[:max_markets]
    print(f"      Checking {len(markets_to_check)} markets\n")

    results = []

    print("[2/3] Analyzing each market...")
    for i, market in enumerate(markets_to_check):
        question    = market["question"]
        market_prob = market["market_prob"]
        yes_token   = market["yes_token"]

        print(f"  [{i+1}/{len(markets_to_check)}] {question[:55]}...")

        try:
            news      = get_news(question)
            ai_result = ask_ai(question, market_prob, news)

            ai_prob    = ai_result["probability"]
            confidence = ai_result["confidence"]
            reasoning  = ai_result["reasoning"]
            edge       = ai_prob - market_prob

            should_trade = (
                abs(edge) >= MINIMUM_EDGE and
                confidence in ["medium", "high"]
            )

            direction = "BUY YES" if edge > 0 else "BUY NO"

            # Always append ALL markets, not just signals
            results.append({
                "question":     question,
                "yes_token":    yes_token,
                "market_prob":  market_prob,
                "ai_prob":      ai_prob,
                "edge":         round(edge, 4),
                "direction":    direction,
                "confidence":   confidence,
                "reasoning":    reasoning,
                "should_trade": should_trade,
            })

            if should_trade:
                print(f"    *** SIGNAL! Market={market_prob:.0%} AI={ai_prob:.0%} Edge={edge:+.0%} -> {direction}")
            else:
                print(f"    No signal. Market={market_prob:.0%} AI={ai_prob:.0%} Edge={edge:+.0%}")

        except Exception as e:
            print(f"    Error: {e}")
            continue

    signals = [r for r in results if r["should_trade"]]
    print(f"\n[3/3] Done! {len(results)} markets analyzed, {len(signals)} signal(s).")
    return results


if __name__ == "__main__":
    results = find_signals(max_markets=5)
    signals = [r for r in results if r["should_trade"]]
    print(f"\nSignals: {len(signals)}")
    for s in signals:
        print(f"  {s['direction']} | {s['edge']:+.0%} | {s['question'][:50]}")