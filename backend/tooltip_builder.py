# /backend/tooltip_builder.py

def build_tooltip(signal: str, stock: dict) -> str:
    s = stock.get("signals", {})
    last = stock.get("last_price")

    if signal == "gap_up":
        return "Opened above prev day high"
    if signal == "gap_down":
        return "Opened below prev day low"
    if signal == "break_above_range":
        hi = stock.get("range_930_940_high")
        return f"Above 9:30–9:40 high: {hi:.2f}" if hi else "Breakout above range"
    if signal == "break_below_range":
        lo = stock.get("range_930_940_low")
        return f"Below 9:30–9:40 low: {lo:.2f}" if lo else "Breakdown below range"
    if signal == "high_rel_vol":
        return f"Relative volume: {stock.get('rel_vol', 0):.2f}x"
    if signal == "momentum_confluence":
        return "Above premarket + prior day levels"

    if signal == "early_move":
        move = s.get("early_move")
        return f"Early move: {move:.2f}%" if move else "Early mover"
    if signal == "squeeze_watch":
        return "High short interest + rel vol + move"
    if signal == "strong_sector":
        return "Sector is outperforming today"
    if signal == "weak_sector":
        return "Sector is underperforming"

    if signal == "near_multi_day_high":
        hi = stock.get("hi_10d")
        return f"{last:.2f} vs 10D High {hi:.2f}" if hi and last else "Near 10D high"
    if signal == "near_multi_day_low":
        lo = stock.get("lo_10d")
        return f"{last:.2f} vs 10D Low {lo:.2f}" if lo and last else "Near 10D low"

    if signal == "top_volume_gainer":
        vol = stock.get("vol_latest")
        return f"Volume: {vol:,}" if vol else "Top volume gainer"
    if signal == "high_volume":
        return "Volume > 2x average"
    if signal == "high_volume_no_breakout":
        return "High vol but still inside range"

    return signal
