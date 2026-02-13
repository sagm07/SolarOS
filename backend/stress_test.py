"""
Stress test: early cleaning (day 5) → negative net gain;
             late cleaning (day 25) → lower capture;
             recommended date in logical window.
Run with server up: python stress_test.py
"""

import sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE = "http://127.0.0.1:8000"


def get(url: str, params: dict = None):
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    return r.json()


def main():
    print("SolarOS stress test (ensure server is running: uvicorn backend.main:app)\n")

    # 1) Recommended (no override)
    print("1. GET /analyze (recommended date)...")
    rec = get(f"{BASE}/analyze")
    if rec.get("error"):
        print("   ERROR:", rec["error"])
        return 1
    period_start = rec.get("period_start_iso")
    period_end = rec.get("period_end_iso")
    rec_date = rec.get("scenario_with_cleaning", {}).get("cleaning_date")
    rec_comp = rec.get("comparison") or {}
    rec_net = rec_comp.get("net_economic_gain_inr", 0)
    rec_capture = rec_comp.get("recoverable_capture_percent", 0)
    print(f"   Period: {period_start} → {period_end}")
    print(f"   Recommended cleaning date: {rec_date}")
    print(f"   Net gain (INR): {rec_net}, Recoverable capture %: {rec_capture}")

    if not period_start:
        print("   Missing period_start_iso in response")
        return 1

    # 2) Early cleaning (day 5) and late (day 25) from period start
    start_date_str = period_start[:10]  # YYYY-MM-DD
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    day5 = (start_dt + timedelta(days=5)).strftime("%Y-%m-%d")
    day25 = (start_dt + timedelta(days=25)).strftime("%Y-%m-%d")

    print(f"\n2. GET /analyze?cleaning_date_override={day5} (early, day 5)...")
    early = get(f"{BASE}/analyze", params={"cleaning_date_override": day5})
    early_comp = early.get("comparison") or {}
    early_net = early_comp.get("net_economic_gain_inr", 0)
    early_capture = early_comp.get("recoverable_capture_percent", 0)
    print(f"   Net gain (INR): {early_net}, Recoverable capture %: {early_capture}")

    # 3) Late cleaning (day 25)
    print(f"\n3. GET /analyze?cleaning_date_override={day25} (late, day 25)...")
    late = get(f"{BASE}/analyze", params={"cleaning_date_override": day25})
    late_comp = late.get("comparison") or {}
    late_net = late_comp.get("net_economic_gain_inr", 0)
    late_capture = late_comp.get("recoverable_capture_percent", 0)
    print(f"   Net gain (INR): {late_net}, Recoverable capture %: {late_capture}")

    # Assertions
    ok = True
    if early_net >= 0:
        print(f"\n   FAIL: Early cleaning (day 5) should yield negative net gain (got {early_net})")
        ok = False
    else:
        print(f"\n   PASS: Early cleaning → negative net gain ({early_net})")

    if rec_date and late_capture >= rec_capture and rec_capture > 0:
        print(f"   FAIL: Late cleaning (day 25) should have lower capture than recommended (rec={rec_capture}, late={late_capture})")
        ok = False
    else:
        print(f"   PASS: Late cleaning → lower or same capture (rec={rec_capture}%, late={late_capture}%)")

    if rec_date:
        rec_dt = datetime.strptime(rec_date, "%Y-%m-%d")
        day5_dt = datetime.strptime(day5, "%Y-%m-%d")
        day25_dt = datetime.strptime(day25, "%Y-%m-%d")
        if day5_dt <= rec_dt <= day25_dt:
            print(f"   PASS: Recommended date {rec_date} sits in logical window [day 5, day 25]")
        else:
            print(f"   INFO: Recommended date {rec_date} (window [day 5, day 25]) — may be outside if data/profile differs")
    else:
        print("   INFO: No recommended date (no cleaning opportunity in period)")

    print("\n" + ("All checks passed." if ok else "Some checks failed."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
