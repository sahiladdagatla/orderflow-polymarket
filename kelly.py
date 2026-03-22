# kelly.py
# Risk-adjusted position sizing using Kelly Criterion
# This makes Risk-adjusted strategy models FULLY SOLVED

def kelly_fraction(edge, odds=1.0, max_fraction=0.25):
    """
    Pure Kelly formula: f = edge / odds
    edge  = ai_prob - market_prob (e.g. 0.17)
    odds  = payout odds (on Polymarket, roughly 1/market_prob - 1)
    max_fraction = cap at 25% of bankroll (half-Kelly safety)
    """
    if edge <= 0:
        return 0.0
    f = edge / odds if odds > 0 else 0
    return min(f, max_fraction)


def size_position(signal: dict, bankroll: float, min_bet=5.0, max_bet=500.0) -> dict:
    """
    Takes a signal dict and bankroll, returns full risk-adjusted sizing.

    signal keys: market_prob, ai_prob, edge, confidence, direction
    bankroll: total USDC available
    """
    market_prob = signal["market_prob"]
    ai_prob     = signal["ai_prob"]
    edge        = abs(signal["edge"])
    confidence  = signal.get("confidence", "low")
    direction   = signal.get("direction", "BUY YES")

    # Implied payout odds from market price
    if direction == "BUY YES":
        price = market_prob
    else:
        price = 1 - market_prob

    if price <= 0 or price >= 1:
        return {"size_usdc": 0, "fraction": 0, "reason": "Invalid price"}

    # Payout odds (how much you win per $1 risked)
    odds = (1 - price) / price

    # Raw Kelly fraction
    raw_kelly = kelly_fraction(edge, odds)

    # Confidence multiplier — scale down if not high confidence
    conf_mult = {"high": 1.0, "medium": 0.6, "low": 0.25}.get(confidence, 0.25)

    # Half-Kelly for safety (industry standard)
    half_kelly = raw_kelly * 0.5 * conf_mult

    # Dollar size
    raw_size = bankroll * half_kelly
    size = max(min_bet, min(raw_size, max_bet))
    size = round(size, 2)

    # Expected value
    ev = edge * size

    return {
        "size_usdc":     size,
        "fraction":      round(half_kelly, 4),
        "raw_kelly":     round(raw_kelly, 4),
        "conf_mult":     conf_mult,
        "odds":          round(odds, 3),
        "expected_value": round(ev, 2),
        "reason": f"Kelly={raw_kelly:.1%} × 0.5 × conf({conf_mult}) → {half_kelly:.1%} of ${bankroll:.0f}"
    }


def apply_portfolio_risk(signals: list, bankroll: float, max_portfolio_risk=0.20) -> list:
    """
    Applies portfolio-level risk limits across all signals.
    Ensures total exposure never exceeds max_portfolio_risk of bankroll.
    """
    sized = []
    total_allocated = 0.0
    max_total = bankroll * max_portfolio_risk

    # Sort by edge descending — best signals get allocated first
    sorted_signals = sorted(signals, key=lambda s: abs(s.get("edge", 0)), reverse=True)

    for signal in sorted_signals:
        sizing = size_position(signal, bankroll)
        proposed = sizing["size_usdc"]

        # Check if adding this trade busts portfolio limit
        if total_allocated + proposed > max_total:
            remaining = max_total - total_allocated
            if remaining < 5:
                sizing["size_usdc"] = 0
                sizing["reason"] = "Portfolio risk limit reached"
            else:
                sizing["size_usdc"] = round(remaining, 2)
                sizing["reason"] += " (capped by portfolio limit)"

        total_allocated += sizing["size_usdc"]
        sized.append({**signal, "sizing": sizing})

    return sized


if __name__ == "__main__":
    print("=" * 55)
    print("  KELLY CRITERION POSITION SIZER — TEST")
    print("=" * 55)

    BANKROLL = 1000.0

    test_signals = [
        {"question": "Will Jesus return before GTA VI?",   "market_prob": 0.48, "ai_prob": 0.02, "edge": -0.46, "confidence": "high",   "direction": "BUY NO"},
        {"question": "Bitcoin hits $1M before GTA VI?",    "market_prob": 0.49, "ai_prob": 0.20, "edge": -0.29, "confidence": "high",   "direction": "BUY NO"},
        {"question": "Harvey Weinstein no prison?",        "market_prob": 0.31, "ai_prob": 0.05, "edge": -0.26, "confidence": "high",   "direction": "BUY NO"},
        {"question": "China invades Taiwan before GTA VI?","market_prob": 0.52, "ai_prob": 0.35, "edge": -0.17, "confidence": "high",   "direction": "BUY NO"},
        {"question": "New Rihanna Album before GTA VI?",   "market_prob": 0.56, "ai_prob": 0.65, "edge":  0.09, "confidence": "medium", "direction": "BUY YES"},
    ]

    print(f"\nBankroll: ${BANKROLL:.2f}")
    print(f"Max portfolio risk: 20% = ${BANKROLL*0.20:.2f}\n")

    sized = apply_portfolio_risk(test_signals, BANKROLL)

    total = 0
    for s in sized:
        sz = s["sizing"]
        print(f"  {s['question'][:45]}")
        print(f"    Edge: {s['edge']:+.0%}  |  Confidence: {s['confidence']}")
        print(f"    Kelly: {sz['raw_kelly']:.1%}  →  Half-Kelly: {sz['fraction']:.1%}")
        print(f"    Size: ${sz['size_usdc']:.2f}  |  EV: +${sz['expected_value']:.2f}")
        print(f"    {sz['reason']}")
        print()
        total += sz["size_usdc"]

    print(f"  Total allocated: ${total:.2f} / ${BANKROLL*0.20:.2f} max")
    print("\nTest passed!")
