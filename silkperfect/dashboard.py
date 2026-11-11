"""Live dashboard: python -m silkperfect dashboard

Opens in your browser. Change a setting in the sidebar and every number and
chart is recalculated from the saved prices, so you can test ideas and see the
result straight away. Nothing here places orders or talks to a broker.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from silkperfect import backtest, config, dataset, scoreboard  # noqa: E402
from silkperfect import walkforward as wf  # noqa: E402
from silkperfect.forecasters import TimesFM, default_forecasters  # noqa: E402

PRIMARY = "TimesFM 2.5"
BASELINE = "No change"

st.set_page_config(page_title="Silkperfect", layout="wide")


@st.cache_data(show_spinner="Loading saved prices...")
def load_prices(symbols: tuple[str, ...]) -> pd.DataFrame:
    return dataset.load_prices(symbols=list(symbols))


@st.cache_data(show_spinner="Running the test...", max_entries=20)
def run_test(symbols: tuple[str, ...], horizon: int, min_history: int, capital: float,
             with_timesfm: bool, _prices: pd.DataFrame) -> scoreboard.Result:
    settings = scoreboard.Settings(horizon=horizon, min_history=min_history, capital=capital)
    forecasters = default_forecasters()
    if with_timesfm:
        forecasters.append(TimesFM(max_context=settings.max_context))
    return scoreboard.run(_prices, list(symbols), settings, forecasters,
                          cache_dir=config.FORECAST_CACHE_DIR)


def pct(value: float, digits: int = 1) -> str:
    return "n/a" if pd.isna(value) else f"{value:+.{digits}f}%"


def sidebar() -> dict:
    st.sidebar.header("Settings")
    universe = config.load_universe()
    chosen = st.sidebar.multiselect("Stocks", universe, default=universe)
    horizon = st.sidebar.slider("Forecast days ahead", 1, 20, config.HORIZON,
                                help="How many trading days ahead each forecast looks.")
    min_history = st.sidebar.slider("Days of history before the first forecast", 250, 800,
                                    config.MIN_HISTORY)
    capital = st.sidebar.number_input("Money per stock (Rs)", 50_000, 5_000_000,
                                      int(config.CAPITAL_PER_SYMBOL), step=50_000)
    with_timesfm = st.sidebar.checkbox(
        "Include TimesFM 2.5", value=True,
        help="Uses saved results when they exist. A new setting makes the first run slow "
             "(about 2 to 3 minutes per stock without a graphics card).")
    st.sidebar.caption("Changing a setting reruns the test. Results for each setting are kept "
                       "until you restart the dashboard.")
    return dict(symbols=tuple(chosen), horizon=horizon, min_history=min_history,
                capital=float(capital), with_timesfm=with_timesfm)


def verdict_section(result: scoreboard.Result, primary: str | None) -> None:
    acc = result.accuracy.set_index("forecaster")
    tr = result.trading.set_index("strategy")
    bh_cagr = tr.loc["Buy and hold", "cagr_pct"]
    st.subheader("Verdict")
    if primary is None:
        st.info("Turn on TimesFM in the sidebar to see its verdict.")
    else:
        skill = acc.loc[primary, "skill_vs_no_change"]
        rule_cagr = tr.loc[f"Forecast rule: {primary}", "cagr_pct"]
        passed = bool(skill > 0 and rule_cagr > bh_cagr)
        cols = st.columns(5)
        cols[0].metric("Forecast skill vs no change", f"{skill:+.4f}",
                       help="Above 0 means better than assuming the price stays where it is.")
        cols[1].metric("Direction right", f"{acc.loc[primary, 'direction_hit_pct']:.1f}%",
                       help="50% is a coin toss.")
        cols[2].metric("Rule, per year after costs", pct(rule_cagr))
        cols[3].metric("Buy and hold, per year", pct(bh_cagr))
        cols[4].metric("Costs paid by the rule",
                       f"Rs {tr.loc[f'Forecast rule: {primary}', 'costs_rupees']:,.0f}")
        if passed:
            st.success(f"{primary} passes the test: better accuracy than no change, and more per year "
                       "after costs than buy and hold.")
        else:
            reasons = []
            if skill <= 0:
                reasons.append("its guesses are not better than no change")
            if rule_cagr <= bh_cagr:
                reasons.append("its trading rule earns less per year than buy and hold")
            st.error(f"{primary} does not pass the test: " + "; ".join(reasons) + ".")
    st.caption(f"Period {result.start:%d %b %Y} to {result.end:%d %b %Y} · {len(result.symbols)} stocks")


def money_tab(result: scoreboard.Result, capital: float) -> None:
    st.caption("Total value of the portfolio, in lakh rupees. Every strategy starts with the same money.")
    series = {}
    for name, curves in result.curves.items():
        series[name] = backtest.combine_equity(curves, capital) / 1e5
    if result.benchmark is not None:
        total = capital * len(result.symbols)
        series[f"{config.BENCHMARK.title()} index (scaled)"] = (
            result.benchmark / result.benchmark.iloc[0] * total / 1e5)
    frame = pd.DataFrame(series).sort_index().ffill()
    st.line_chart(frame, height=460)


def accuracy_tab(result: scoreboard.Result) -> None:
    acc = result.accuracy[result.accuracy["forecaster"] != BASELINE].set_index("forecaster")
    st.caption("Skill against no change, over every stock and every day. Above 0 is better than "
               "assuming the price stays where it is.")
    st.bar_chart(acc[["skill_vs_no_change"]].rename(columns={"skill_vs_no_change": "skill"}), height=300)
    st.dataframe(acc[["forecasts", "mae_pct", "skill_vs_no_change", "direction_hit_pct",
                      "symbols_beaten"]].round(4), use_container_width=True)
    st.subheader("Skill by year")
    by_year = result.skill_by_year[result.skill_by_year["forecaster"] != BASELINE].set_index("forecaster")
    st.dataframe(by_year.round(4), use_container_width=True)


def trading_tab(result: scoreboard.Result) -> None:
    st.caption("After costs. Buy and hold is the bar to beat; the index row ignores costs and dividends.")
    st.dataframe(result.trading.round(2).set_index("strategy"), use_container_width=True)


def stock_tab(result: scoreboard.Result, settings_cols: dict, primary: str | None) -> None:
    symbol = st.selectbox("Stock", list(result.symbols))
    close = result.closes[symbol].loc[result.start:result.end]
    rule_name = f"Forecast rule: {primary}" if primary else None

    left, right = st.columns([3, 2])
    with left:
        st.caption("Actual close, and the price the forecaster expected 5 days later (drawn on the day it was for).")
        chart = pd.DataFrame({"Actual close": close})
        if primary:
            frame = result.forecasts[symbol][primary]
            pos = result.closes[symbol].index.get_indexer(frame.index) + settings_cols["horizon"]
            ok = pos < len(result.closes[symbol])
            target = pd.Series(frame["pred_price"].to_numpy()[ok],
                               index=result.closes[symbol].index[pos[ok]])
            chart[f"{primary} guess"] = target.reindex(chart.index)
        st.line_chart(chart, height=380)

    with right:
        if primary:
            frame = result.forecasts[symbol][primary]
            last = frame.iloc[-1]
            entry = result.entry_threshold
            holding = bool(wf.forecast_signal(frame["pred_ret"], entry).iloc[-1])
            st.metric(f"Last close ({frame.index[-1]:%d %b %Y})", f"Rs {last['close']:,.2f}")
            st.metric(f"{primary}'s guess in {settings_cols['horizon']} trading days",
                      f"Rs {last['pred_price']:,.2f}",
                      pct((last["pred_price"] / last["close"] - 1) * 100, 2))
            st.metric("Rule today", "BUY (holding)" if holding else "CASH")
            scored = frame.dropna(subset=["actual_ret"])
            if len(scored) > 2:
                r = np.corrcoef(scored["pred_ret"], scored["actual_ret"])[0, 1]
                st.metric("Guess vs reality (correlation)", f"{r:+.2f}",
                          help="Near 0 means the guesses say little about what happened.")
            st.caption("Each dot is one day: what was predicted (across) against what happened (up).")
            sample = scored.sample(min(len(scored), 1500), random_state=0)
            st.scatter_chart(pd.DataFrame({"predicted %": sample["pred_ret"] * 100,
                                           "actual %": sample["actual_ret"] * 100}),
                             x="predicted %", y="actual %", height=260)

    st.subheader("Trades")
    rows = result.by_symbol[result.by_symbol["symbol"] == symbol].set_index("strategy")
    st.dataframe(rows[["total_return_pct", "cagr_pct", "max_drawdown_pct", "trades", "costs_rupees"]]
                 .round(2), use_container_width=True)
    if rule_name and rule_name in result.trade_logs and symbol in result.trade_logs[rule_name]:
        log = result.trade_logs[rule_name][symbol]
        if len(log):
            st.caption(f"Trades made by the {primary} rule (fills at the next day's open)")
            st.dataframe(log[["EntryTime", "EntryPrice", "ExitTime", "ExitPrice", "Size"]]
                         .round(2), use_container_width=True)


def main() -> None:
    st.title("Silkperfect: are the forecasts good enough to trade?")
    settings = sidebar()
    if not settings["symbols"]:
        st.warning("Choose at least one stock in the sidebar.")
        return
    if not config.PRICES_PATH.exists():
        st.error("No saved prices yet. Run `python -m silkperfect build` first.")
        return

    symbols = settings["symbols"] + (config.BENCHMARK,)
    prices = load_prices(symbols)
    try:
        result = run_test(settings["symbols"], settings["horizon"], settings["min_history"],
                          settings["capital"], settings["with_timesfm"], prices)
    except SystemExit as exc:
        # TimesFM raises SystemExit when it is not installed; Streamlit would hide that silently.
        st.error(f"{exc} (or untick 'Include TimesFM 2.5' in the sidebar to see the simple rules only.)")
        return

    primary = PRIMARY if PRIMARY in set(result.accuracy["forecaster"]) else None
    verdict_section(result, primary)

    money, accuracy, trading, stock = st.tabs(["Money over time", "Accuracy", "Trades after costs", "Per stock"])
    with money:
        money_tab(result, settings["capital"])
    with accuracy:
        accuracy_tab(result)
    with trading:
        trading_tab(result)
    with stock:
        stock_tab(result, settings, primary)


main()
