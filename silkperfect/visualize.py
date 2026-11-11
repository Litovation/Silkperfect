"""Visual report: python -m silkperfect visualize  ->  reports/visualizer.html

One self-contained HTML file: charts are plain SVG, so it opens offline in any
browser. It reads the same results the scoreboard uses, so the pictures and the
numbers always agree.
"""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import backtest, config, walkforward as wf
from .scoreboard import Result, Settings

PRIMARY = "TimesFM 2.5"          # the forecaster the per-stock pages focus on
BASELINE = "No change"

COLORS = {
    "Buy and hold": "#2563eb",
    "Moving-average crossover": "#7c3aed",
    "Forecast rule: No change": "#94a3b8",
    "Forecast rule: Drift": "#ea580c",
    "Forecast rule: Moving average": "#ca8a04",
    "Forecast rule: TimesFM": "#dc2626",
}
INDEX_COLOR = "#475569"
FALLBACK = ["#0f766e", "#be185d", "#4f46e5", "#65a30d"]


def esc(value) -> str:
    return html.escape(str(value))


def color_for(name: str) -> str:
    for key, color in COLORS.items():
        if name.startswith(key):
            return color
    if "index" in name.lower():
        return INDEX_COLOR
    return FALLBACK[sum(map(ord, name)) % len(FALLBACK)]


def fmt(value, spec: str = "") -> str:
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return "n/a"
    return format(value, spec)


def signed_class(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return "pos" if value > 0 else ("neg" if value < 0 else "")


def years(index) -> np.ndarray:
    """Dates as fractional years, for the horizontal axis."""
    idx = pd.DatetimeIndex(pd.to_datetime(index))
    return idx.year.to_numpy(dtype=float) + (idx.day_of_year.to_numpy(dtype=float) - 1) / 365.25


def thin(n: int, limit: int = 900) -> np.ndarray:
    """Evenly spaced positions, so charts stay light for ~2,000 daily points."""
    return np.arange(n) if n <= limit else np.unique(np.linspace(0, n - 1, limit).astype(int))


def legend(items: list[tuple[str, str]]) -> str:
    spans = "".join(f'<span><i style="background:{c}"></i>{esc(name)}</span>' for name, c in items)
    return f'<div class="legend">{spans}</div>'


def line_chart(lines: list[dict], markers: list[dict] = (), *, y_fmt=lambda v: f"{v:,.0f}",
               zero_line: bool = False, width: int = 960, height: int = 330) -> str:
    """lines: dicts with x, y, color, dash. markers: dicts with x, y, color, up."""
    left, right, top, bottom = 74, 16, 14, 30
    xs = np.concatenate([np.asarray(l["x"], float) for l in lines])
    ys = [np.asarray(l["y"], float) for l in lines] + [np.asarray(m["y"], float) for m in markers]
    ys = np.concatenate(ys + ([np.array([0.0])] if zero_line else []))
    xs = xs[np.isfinite(xs)]
    ys = ys[np.isfinite(ys)]
    x0, x1 = float(xs.min()), float(xs.max())
    lo, hi = float(ys.min()), float(ys.max())
    if hi - lo < 1e-9:
        hi = lo + 1
    pad = (hi - lo) * 0.06
    lo, hi = lo - pad, hi + pad

    def sx(v):
        return left + (v - x0) / max(x1 - x0, 1e-9) * (width - left - right)

    def sy(v):
        return top + (1 - (v - lo) / (hi - lo)) * (height - top - bottom)

    out = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img">']
    for t in np.linspace(lo, hi, 5):
        y = sy(t)
        out.append(f'<line x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" class="tick" text-anchor="end">{esc(y_fmt(t))}</text>')
    if zero_line and lo < 0 < hi:
        out.append(f'<line x1="{left}" x2="{width - right}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" class="zero"/>')
    for yr in range(int(np.ceil(x0)), int(np.floor(x1)) + 1):
        x = sx(yr)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{height - bottom}" class="grid"/>')
        out.append(f'<text x="{x:.1f}" y="{height - 10}" class="tick" text-anchor="middle">{yr}</text>')
    for l in lines:
        x, y = np.asarray(l["x"], float), np.asarray(l["y"], float)
        ok = np.isfinite(x) & np.isfinite(y)
        x, y = x[ok], y[ok]
        sel = thin(len(x))
        pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(x[sel], y[sel]))
        dash = ' stroke-dasharray="6 4"' if l.get("dash") else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{l["color"]}" '
                   f'stroke-width="{l.get("width", 1.8)}"{dash}/>')
    for m in markers:
        x, y = np.asarray(m["x"], float), np.asarray(m["y"], float)
        ok = np.isfinite(x) & np.isfinite(y)
        for a, b in zip(x[ok], y[ok]):
            px, py = sx(a), sy(b)
            if m["up"]:
                pts = f"{px:.1f},{py - 7:.1f} {px - 5:.1f},{py + 3:.1f} {px + 5:.1f},{py + 3:.1f}"
            else:
                pts = f"{px:.1f},{py + 7:.1f} {px - 5:.1f},{py - 3:.1f} {px + 5:.1f},{py - 3:.1f}"
            out.append(f'<polygon points="{pts}" fill="{m["color"]}" opacity="0.9"/>')
    out.append("</svg>")
    return "".join(out)


def scatter_chart(x: np.ndarray, y: np.ndarray, *, width: int = 460, height: int = 330) -> str:
    """Predicted 5-day change (x) against what actually happened (y), in percent."""
    left, right, top, bottom = 52, 14, 14, 36
    lim = max(float(np.nanmax(np.abs(np.concatenate([x, y])))) * 1.05, 1.0)

    def sx(v):
        return left + (v + lim) / (2 * lim) * (width - left - right)

    def sy(v):
        return top + (1 - (v + lim) / (2 * lim)) * (height - top - bottom)

    out = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img">']
    for t in (-lim, 0.0, lim):
        out.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{top}" y2="{height - bottom}" class="grid"/>')
        out.append(f'<line x1="{left}" x2="{width - right}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" class="grid"/>')
        out.append(f'<text x="{sx(t):.1f}" y="{height - 18}" class="tick" text-anchor="middle">{t:+.0f}%</text>')
        out.append(f'<text x="{left - 6}" y="{sy(t) + 4:.1f}" class="tick" text-anchor="end">{t:+.0f}%</text>')
    out.append(f'<line x1="{sx(-lim):.1f}" y1="{sy(-lim):.1f}" x2="{sx(lim):.1f}" y2="{sy(lim):.1f}" class="diag"/>')
    for a, b in zip(x, y):
        out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="2.2" class="dot"/>')
    out.append(f'<text x="{(left + width - right) / 2:.0f}" y="{height - 2}" class="tick" text-anchor="middle">'
               "Predicted 5-day change</text>")
    out.append(f'<text x="12" y="{(top + height - bottom) / 2:.0f}" class="tick" text-anchor="middle" '
               f'transform="rotate(-90 12 {(top + height - bottom) / 2:.0f})">Actual 5-day change</text>')
    out.append("</svg>")
    return "".join(out)


def bars(items: list[tuple[str, float, str]], fmt_spec: str = "+.4f") -> str:
    """Horizontal bars centred on zero. items: (label, value, color)."""
    scale = max((abs(v) for _, v, _ in items if not pd.isna(v)), default=1.0) or 1.0
    rows = []
    for label, value, color in items:
        if pd.isna(value):
            width, left, text = 0.0, 50.0, "n/a"
        else:
            width = abs(value) / scale * 50
            left = 50.0 if value >= 0 else 50.0 - width
            text = format(value, fmt_spec)
        rows.append(f'<div class="bar"><span>{esc(label)}</span><div class="track">'
                    f'<div class="fill" style="left:{left:.1f}%;width:{width:.1f}%;background:{color}"></div>'
                    f'</div><span class="val {signed_class(value)}">{esc(text)}</span></div>')
    return "".join(rows)


def html_table(headers: list[str], rows: list[list[tuple[str, str]]]) -> str:
    """rows: lists of (html_text, css_class) cells."""
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f'<td class="{c}">{t}</td>' for t, c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def card(label: str, value: str, css: str = "", note: str = "") -> str:
    note_html = f'<span>{esc(note)}</span>' if note else ""
    return f'<div class="card"><b class="{css}">{esc(value)}</b><span>{esc(label)}</span>{note_html}</div>'


def stock_section(result: Result, sym: str, settings: Settings, entry: float, bh: str, rule: str) -> str:
    closes = result.closes[sym]
    frame = result.forecasts[sym][PRIMARY]
    window_close = closes.loc[result.start:result.end]

    # A forecast made on day t is for day t + horizon: plot it on that day.
    pos = closes.index.get_indexer(frame.index) + settings.horizon
    valid = pos < len(closes)
    target = pd.Series(frame["pred_price"].to_numpy()[valid], index=closes.index[pos[valid]])
    target = target.loc[result.start:result.end]

    markers = []
    log = result.trade_logs.get(rule, {}).get(sym)
    if log is not None and len(log):
        markers.append({"x": years(pd.to_datetime(log["EntryTime"])),
                        "y": log["EntryPrice"].to_numpy(float), "color": "#16a34a", "up": True})
        markers.append({"x": years(pd.to_datetime(log["ExitTime"])),
                        "y": log["ExitPrice"].to_numpy(float), "color": "#dc2626", "up": False})
    price_chart = line_chart(
        [{"x": years(window_close.index), "y": window_close.to_numpy(), "color": "#111827", "width": 1.6},
         {"x": years(target.index), "y": target.to_numpy(), "color": color_for(rule),
          "width": 1.2, "dash": True}],
        markers, y_fmt=lambda v: f"Rs {v:,.0f}")

    scored = frame.dropna(subset=["actual_ret"])
    px = scored["pred_ret"].to_numpy() * 100
    ay = scored["actual_ret"].to_numpy() * 100
    r = float(np.corrcoef(px, ay)[0, 1]) if len(px) > 2 else float("nan")
    sel = thin(len(px), 700)
    scatter = scatter_chart(px[sel], ay[sel])

    last = frame.iloc[-1]
    change = (last["pred_price"] / last["close"] - 1) * 100
    holding = bool(wf.forecast_signal(frame["pred_ret"], entry).iloc[-1])
    stance = "holding the stock" if holding else "staying in cash"

    rows = result.by_symbol[result.by_symbol["symbol"] == sym].set_index("strategy")
    table = html_table(
        ["Strategy", "Total return (%)", "Per year (%)", "Worst drop (%)", "Trades", "Costs (Rs)"],
        [[(name, ""),
          (fmt(rows.loc[name, "total_return_pct"], "+.1f"), signed_class(rows.loc[name, "total_return_pct"])),
          (fmt(rows.loc[name, "cagr_pct"], "+.1f"), signed_class(rows.loc[name, "cagr_pct"])),
          (fmt(rows.loc[name, "max_drawdown_pct"], ".1f"), ""),
          (fmt(int(rows.loc[name, "trades"]), ","), ""),
          (fmt(rows.loc[name, "costs_rupees"], ",.0f"), "")]
         for name in (bh, rule) if name in rows.index])

    corr_text = f"{r:+.2f}" if not np.isnan(r) else "n/a"
    return f"""
<section class="stock" data-sym="{esc(sym)}" hidden>
  <h3>{esc(sym)}</h3>
  <div class="cards">
    {card("Last close", f"Rs {last['close']:,.2f}", note=f"{frame.index[-1]:%d %b %Y}")}
    {card("TimesFM's guess in 5 trading days", f"Rs {last['pred_price']:,.2f}", note=f"{change:+.2f}% from last close")}
    {card("Rule today", "BUY" if holding else "CASH", "pos" if holding else "", note=f"The rule says {stance}")}
    {card("Guess vs reality (correlation)", corr_text, note="near 0 = no link between the guess and what happened")}
  </div>
  <h4>Price, and where TimesFM expected it to be 5 days later</h4>
  <p class="note">Dark line: actual close. Dashed orange: TimesFM's 5-day-ahead guess, drawn on the day it was for.
  Green triangles: the rule buys. Red triangles: the rule sells.</p>
  {price_chart}
  {legend([("Actual close", "#111827"), ("TimesFM guess for 5 days later", color_for(rule)), ("Rule buy", "#16a34a"), ("Rule sell", "#dc2626")])}
  <div class="two">
    <div>
      <h4>Guess vs reality</h4>
      <p class="note">Each dot is one day. Across: what TimesFM predicted. Up: what really happened.
      If the guesses were useful the dots would lean up-right along the dashed line. They scatter instead.</p>
      {scatter}
    </div>
    <div>
      <h4>Results for this stock (after costs)</h4>
      {table}
      <p class="note">Each stock starts with Rs {settings.capital:,.0f}.</p>
    </div>
  </div>
</section>"""


def build_html(result: Result, settings: Settings, events: pd.DataFrame | None = None) -> str:
    acc = result.accuracy.set_index("forecaster")
    tr = result.trading.set_index("strategy")
    bh = "Buy and hold"
    index_rows = [n for n in tr.index if "index" in n.lower()]
    forecasters = [f for f in acc.index if f != BASELINE]
    primary = PRIMARY if PRIMARY in forecasters else (forecasters[-1] if forecasters else None)
    entry = result.entry_threshold
    capital_total = settings.capital * len(result.symbols)

    # 1. Verdict
    verdict_rows = []
    bh_cagr = tr.loc[bh, "cagr_pct"]
    for f in forecasters:
        skill = acc.loc[f, "skill_vs_no_change"]
        rule = f"Forecast rule: {f}"
        rcagr = tr.loc[rule, "cagr_pct"] if rule in tr.index else float("nan")
        passed = bool(skill > 0 and rcagr > bh_cagr)
        verdict_rows.append([
            (esc(f), ""),
            (fmt(skill, "+.4f"), signed_class(skill)),
            (fmt(acc.loc[f, "direction_hit_pct"], ".1f") + "%", ""),
            (fmt(rcagr, "+.1f") + "%", signed_class(rcagr)),
            (fmt(bh_cagr, "+.1f") + "%", ""),
            ("PASSES" if passed else "FAILS", "yes" if passed else "no"),
        ])
    verdict_table = html_table(
        ["Forecaster", "Skill vs no change", "Direction right", "Rule, per year after costs",
         "Buy and hold, per year", "Passes the test?"], verdict_rows)

    cards = ""
    if primary:
        skill = acc.loc[primary, "skill_vs_no_change"]
        rcagr = tr.loc[f"Forecast rule: {primary}", "cagr_pct"]
        cards = "".join([
            card("Forecast skill vs no change", fmt(skill, "+.4f"), "neg" if skill < 0 else "pos",
                 "above 0 means better than assuming no change"),
            card("Direction right", fmt(acc.loc[primary, "direction_hit_pct"], ".1f") + "%",
                 note="50% is a coin toss"),
            card(f"{primary} rule, per year", fmt(rcagr, "+.1f") + "%", signed_class(rcagr),
                 "after costs"),
            card("Buy and hold, per year", fmt(bh_cagr, "+.1f") + "%", note="after costs, no forecasts"),
            card(f"Costs paid by the {primary} rule",
                 f"Rs {tr.loc[f'Forecast rule: {primary}', 'costs_rupees']:,.0f}",
                 note=f"{int(tr.loc[f'Forecast rule: {primary}', 'trades']):,} trades"),
        ])

    # 2. Equity curves
    eq_lines, eq_legend = [], []
    for name, curves in result.curves.items():
        port = backtest.combine_equity(curves, settings.capital)
        color = color_for(name)
        eq_lines.append({"x": years(port.index), "y": port.to_numpy() / 1e5, "color": color})
        eq_legend.append((name, color))
    if result.benchmark is not None and index_rows:
        b = result.benchmark / result.benchmark.iloc[0] * capital_total
        eq_lines.append({"x": years(b.index), "y": b.to_numpy() / 1e5, "color": INDEX_COLOR,
                         "dash": True, "width": 1.5})
        eq_legend.append((f"{index_rows[0]} (scaled to the same start)", INDEX_COLOR))
    equity_chart = line_chart(eq_lines, y_fmt=lambda v: f"Rs {v:,.0f}L")

    # 3. Accuracy bars
    skill_bars = bars([(f, acc.loc[f, "skill_vs_no_change"], color_for(f"Forecast rule: {f}"))
                       for f in forecasters])

    # 4. Skill by year
    sby = result.skill_by_year
    sby = sby[sby["forecaster"] != BASELINE]
    years_cols = [c for c in sby.columns if c != "forecaster"]
    year_table = html_table(
        ["Forecaster"] + years_cols,
        [[(esc(r["forecaster"]), "")] + [(fmt(r[y], "+.4f"), signed_class(r[y])) for y in years_cols]
         for _, r in sby.iterrows()])

    # 5. Trading table
    trade_table = html_table(
        ["Strategy", "Total return (%)", "Per year (%)", "Worst drop (%)", "Trades", "Costs (Rs)", "Time invested (%)"],
        [[(esc(r["strategy"]), ""),
          (fmt(r["total_return_pct"], "+.1f"), signed_class(r["total_return_pct"])),
          (fmt(r["cagr_pct"], "+.1f"), signed_class(r["cagr_pct"])),
          (fmt(r["max_drawdown_pct"], ".1f"), ""),
          (fmt(int(r["trades"]), ","), ""),
          (fmt(r["costs_rupees"], ",.0f"), ""),
          (fmt(r["exposure_pct"], ".0f"), "")]
         for _, r in result.trading.iterrows()])

    # 6. Per-stock explorer
    stock_html, options = [], []
    rule_name = f"Forecast rule: {primary}" if primary else None
    for sym in result.symbols:
        options.append(f'<option value="{esc(sym)}">{esc(sym)}</option>')
        if primary and sym in result.forecasts and primary in result.forecasts[sym]:
            stock_html.append(stock_section(result, sym, settings, entry, bh, rule_name))
    stock_html = "".join(stock_html)
    stock_block = (f'<div class="box"><label>Stock: <select id="sym">{"".join(options)}</select></label></div>'
                   f"{stock_html}") if stock_html else '<p class="note">No per-stock charts for this run.</p>'

    # 7. Data checks
    notes = []
    if events is not None and len(events):
        mine = events[events["symbol"].isin(result.symbols)]
        review = mine[mine["status"].isin(("unconfirmed", "unparsed"))]
        notes.append(f"{len(review)} corporate-action events could not be applied and need a manual look.")
        for _, e in review.head(20).iterrows():
            notes.append(f"{e['symbol']} {e['ex_date']:%d %b %Y}: {e['purpose']} ({e['status']})")
    notes_html = "".join(f"<li>{esc(n)}</li>" for n in notes)

    generated = datetime.now().strftime("%d %b %Y, %H:%M")
    period = f"{result.start:%d %b %Y} to {result.end:%d %b %Y}"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Silkperfect visualizer</title>
<style>{CSS}</style></head>
<body><main>
<h1>Silkperfect: are the forecasts good enough to trade?</h1>
<p class="muted">Period judged: {esc(period)} · {len(result.symbols)} stocks · Rs {settings.capital:,.0f} per stock ·
forecasts {settings.horizon} trading days ahead · generated {esc(generated)}</p>

<div class="box">
  <h4>In plain words</h4>
  <ul>
    <li>The program looks at each stock's past prices day by day. On each day it asks a forecaster
    (a simple rule, or TimesFM 2.5) for the price 5 trading days ahead.</li>
    <li>The <b>skill</b> number compares those guesses with the simplest guess of all: "tomorrow looks like today".
    Above 0 is better than that. Below 0 is worse.</li>
    <li>The <b>rule</b> turns guesses into trades: buy when the guess is high enough to cover the trading costs,
    sell when it turns negative. Every trade pays brokerage, taxes and slippage.</li>
    <li>A strategy only counts as useful if it beats simply holding the stocks, after costs.</li>
  </ul>
</div>

<h2>1. The verdict</h2>
<div class="cards">{cards}</div>
{verdict_table}
<p class="note">The pass test is simple and was set before the run: the forecast must beat "no change" on accuracy,
and the trading rule must earn more per year after costs than buy and hold.</p>

<h2>2. Money over time</h2>
<p class="note">Total value of the portfolio in lakh rupees. Each strategy starts with the same money.</p>
{equity_chart}
{legend(eq_legend)}

<h2>3. How accurate are the guesses?</h2>
<p class="note">Skill against "no change", across all stocks and all days. Bars right of the line are better than no change.</p>
{skill_bars}
<h4>Skill by year</h4>
{year_table}

<h2>4. Trading results after costs</h2>
{trade_table}

<h2>5. Per stock</h2>
<p class="note">Pick a stock. Charts show the actual price, the TimesFM guess, and the trades its rule made.</p>
{stock_block}

<h2>6. Data checks</h2>
<ul>{notes_html or "<li>No corporate-action events to report.</li>"}</ul>
<p class="note">The adjusted prices, forecasts and trade logs come from the same run as <code>reports/scoreboard.md</code>.
Not financial advice: a research tool, and past results do not predict future returns.</p>
</main>
<script>
const sel = document.getElementById('sym');
function showStock() {{
  for (const d of document.querySelectorAll('.stock')) d.hidden = d.dataset.sym !== sel.value;
}}
if (sel) {{ sel.addEventListener('change', showStock); showStock(); }}
</script>
</body></html>"""


CSS = """
:root{--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--bg:#f5f7fb;--card:#fff;--pos:#15803d;--neg:#b91c1c;--accent:#2563eb}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#e5e7eb;--muted:#9ca3af;--line:#334155;--bg:#0f172a;--card:#1e293b;--pos:#4ade80;--neg:#f87171;--accent:#60a5fa}}
:root[data-theme="dark"]{--ink:#e5e7eb;--muted:#9ca3af;--line:#334155;--bg:#0f172a;--card:#1e293b;--pos:#4ade80;--neg:#f87171;--accent:#60a5fa}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1040px;margin:0 auto;padding:24px 16px 60px}
h1{font-size:26px;margin:0 0 4px} h2{font-size:20px;margin:36px 0 8px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:20px;margin:0 0 8px} h4{font-size:15px;margin:18px 0 4px}
.muted,.note{color:var(--muted);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.card b{display:block;font-size:22px} .card span{display:block;color:var(--muted);font-size:12px}
.pos{color:var(--pos)!important} .neg{color:var(--neg)!important}
.yes{color:var(--pos);font-weight:600} .no{color:var(--neg);font-weight:600}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:13px;margin:8px 0;display:block;overflow-x:auto}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap} th:first-child,td:first-child{text-align:left}
svg.chart{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:6px 0}
.grid{stroke:var(--line)} .zero{stroke:var(--muted);stroke-width:1.2} .tick{fill:var(--muted);font-size:12px}
.dot{fill:var(--accent);opacity:.35} .diag{stroke:var(--muted);stroke-dasharray:4 4}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;margin:6px 0} .legend i{display:inline-block;width:14px;height:3px;margin-right:6px;vertical-align:middle}
.bar{display:grid;grid-template-columns:260px 1fr 80px;align-items:center;gap:8px;margin:6px 0;font-size:14px}
.track{position:relative;height:16px;background:var(--line);border-radius:4px}
.track::after{content:"";position:absolute;left:50%;top:-3px;bottom:-3px;width:2px;background:var(--muted)}
.fill{position:absolute;top:0;bottom:0;border-radius:4px} .val{text-align:right;font-variant-numeric:tabular-nums}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:760px){.two{grid-template-columns:1fr}.bar{grid-template-columns:1fr 1fr}.bar .track{grid-column:1/3}}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}
.box h4{margin-top:0} .box ul{margin:0;padding-left:20px}
select{font-size:15px;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink)}
[hidden]{display:none!important}
"""


def save(page: str, path: Path = config.REPORTS_DIR / "visualizer.html") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return path
