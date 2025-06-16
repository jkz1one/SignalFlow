import os
import json
import sys

# Resolve cache directory relative to this script
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")


def build_autowatchlist(scored_path=None):
    """
    Build the autowatchlist from the most recent scored universe file.
    Includes only symbols with score >= 3 and no risk blocks.
    """
    # Determine scored file path
    if scored_path is None:
        files = [f for f in os.listdir(CACHE_DIR)
                 if f.startswith("universe_scored_") and f.endswith(".json")]
        if not files:
            raise FileNotFoundError("No scored universe file found in cache.")
        # pick latest by modification time
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)),
            reverse=True
        )
        scored_path = os.path.join(CACHE_DIR, files[0])

    # Load scored universe
    with open(scored_path, "r") as f:
        universe = json.load(f)

    watchlist = {}
    for symbol, info in universe.items():
        score = info.get("score", 0)
        signals = info.get("signals", {})

        # Identify risk reasons
        reasons = []
        if signals.get("low_liquidity"):
            reasons.append("Low Liquidity")
        if signals.get("wide_spread"):
            reasons.append("Wide Spread")
        is_blocked = len(reasons) > 0

        # Include only if meets score threshold and not blocked
        if score >= 3 and not is_blocked:
            tags = []
            # Tier 1: Strong Setup if ≥2 core signals
            t1_signals = [
                "gap_up",
                "gap_down",
                "break_above_range",
                "break_below_range",
                "high_rel_vol"
            ]
            t1_hits = sum(1 for k in t1_signals if signals.get(k))
            if t1_hits >= 2:
                tags.append("Strong Setup")

            # Tier 2: Squeeze Watch
            if signals.get("squeeze_watch"):
                tags.append("Squeeze Watch")
            # Tier 2: Early % Move
            if signals.get("early_move"):
                tags.append("Early Watch")

            # attach metadata
            info["tags"] = tags
            info["isBlocked"] = is_blocked
            info["reasons"] = reasons

            # ✅ Construct final dict with screeners included
            watchlist[symbol] = {
                "score": score,
                "tierHits": info.get("tierHits", {}),
                "reasons": info.get("reasons", []),
                "screeners": info.get("screeners", []),
                "level": info.get("level"),
                "sector": info.get("sector"),
                "tags": tags,
                "signals": signals,
                "isBlocked": is_blocked
            }

    # Dump autowatchlist cache
    out_path = os.path.join(CACHE_DIR, "autowatchlist_cache.json")
    with open(out_path, "w") as f:
        json.dump(watchlist, f, indent=2)

    return watchlist


if __name__ == "__main__":
    # Optional custom scored file path
    scored_arg = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        result = build_autowatchlist(scored_arg)
        print(f"✅ AutoWatchlist built with {len(result)} entries.")
    except Exception as e:
        print(f"Error building AutoWatchlist: {e}", file=sys.stderr)
        sys.exit(1)
