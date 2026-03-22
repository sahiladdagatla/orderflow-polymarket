import time
from find_signals import find_signals

SCAN_EVERY_MINUTES = 5

print("=" * 55)
print("  POLYMARKET SIGNAL BOT")
print(f"  Scanning every {SCAN_EVERY_MINUTES} minutes")
print("  Press Ctrl+C to stop")
print("=" * 55)

scan_number = 0

while True:
    scan_number += 1
    print(f"\nSCAN #{scan_number} at {time.strftime('%H:%M:%S')}")

    signals = find_signals(max_markets=10)

    if signals:
        print(f"\n  {len(signals)} signal(s) found!")
        for s in signals:
            print(f"  -> {s['direction']} | {s['edge']:+.0%} edge | {s['question'][:45]}...")
    else:
        print("  No signals this scan.")

    print(f"\n  Waiting {SCAN_EVERY_MINUTES} minutes...")
    time.sleep(SCAN_EVERY_MINUTES * 60)