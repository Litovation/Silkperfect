"""Silkperfect dashboard.  Start it with:  streamlit run dashboard.py

The first page explains, in plain words, what a sum of money would have
become under a plan, and runs a pretend account. The other pages hold the
detailed tests.
"""
from __future__ import annotations

import importlib.util

import altair as alt
import pandas as pd
import streamlit as st

from silkperfect import config, dataset, paper, parse, ranking, scoreboard
from silkperfect.forecasters import TimesFM, default_forecasters

alt.data_transformers.disable_max_rows()

# Chart colours. Each line keeps its colour whichever other lines are shown.
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BENCHMARK_COLOUR = "#898781"
GOOD, BAD = "#006300", "#d03b3b"
CASH_RULE = "Forecast rule: No change"   # never trades, so it is left off charts


def colour_map(names: list[str]) -> dict[str, str]:
    """Fixed colour per known line; anything new takes the next free slot."""
    known = ["Buy and hold", "Moving-average crossover", "Forecast rule: Drift",
             "Forecast rule: Moving average", "Forecast rule: TimesFM"]
    out, used = {}, set()
    for name in names:
        if name == scoreboard.BENCHMARK_LABEL:
            out[name] = BENCHMARK_COLOUR
            continue
        slot = next((i for i, k in enumerate(known) if name.startswith(k)), None)
        if slot is None:
            slot = next(i for i in range(len(known), len(SLOTS)) if i not in used)
        used.add(slot)
        out[name] = SLOTS[slot]
    return out


def timesfm_installed() -> bool:
    return all(importlib.util.find_spec(m) for m in ("timesfm", "torch"))


@st.cache_data(show_spinner="Loading prices ...")
def load_prices(symbols: tuple[str, ...], stamp: float) -> pd.DataFrame:
    return dataset.load_prices(symbols=list(symbols))


@st.cache_data(show_spinner=False)
def all_symbols(stamp: float) -> list[str]:
    df = pd.read_parquet(config.PRICES_PATH, columns=["symbol", "series"])
    return sorted(df.loc[df["series"] != parse.INDEX_SERIES, "symbol"].unique())


@st.cache_data(show_spinner=False)
def last_data_day(stamp: float) -> pd.Timestamp:
    return pd.read_parquet(config.PRICES_PATH, columns=["date"])["date"].max()


def line_chart(df: pd.DataFrame, value: str, title: str, fmt: str, colours: dict[str, str],
               dashed: tuple[str, ...] = (), axis_fmt: str | None = None) -> alt.LayerChart:
    """Lines with a legend, a crosshair and a tooltip listing every line's value."""
    names = list(colours)
    base = alt.Chart(df).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(grid=False, labelColor=MUTED, tickColor=GRID,
                                                    domainColor=GRID)),
        color=alt.Color("series:N", sort=names,
                        scale=alt.Scale(domain=names, range=[colours[n] for n in names]),
                        legend=alt.Legend(title=None, orient="top", labelColor=INK,
                                          labelLimit=320, symbolStrokeWidth=3, columns=3)))
    lines = base.mark_line(strokeWidth=2).encode(
        y=alt.Y(f"{value}:Q", title=title, scale=alt.Scale(zero=False),
                axis=alt.Axis(format=axis_fmt or fmt, gridColor=GRID, labelColor=MUTED, titleColor=MUTED,
                              domain=False, ticks=False)),
        strokeDash=alt.condition(alt.FieldOneOfPredicate("series", list(dashed)),
                                 alt.value([5, 4]), alt.value([1, 0])))
    hover = alt.selection_point(fields=["date"], nearest=True, on="pointerover", empty=False)
    # Column names such as "Forecast rule: Drift" contain characters Altair
    # reads as syntax, so the tooltip uses plain keys and shows the real name as its title.
    wide = df.pivot_table(index="date", columns="series", values=value)
    present = [n for n in names if n in wide.columns]
    keys = {n: f"s{i}" for i, n in enumerate(present)}
    wide = wide[present].rename(columns=keys).reset_index()
    rule = (alt.Chart(wide).mark_rule(color=MUTED)
            .encode(x="date:T",
                    opacity=alt.condition(hover, alt.value(0.6), alt.value(0)),
                    tooltip=[alt.Tooltip("date:T", title="Date", format="%d %b %Y")]
                    + [alt.Tooltip(f"{keys[n]}:Q", title=n, format=fmt) for n in present])
            .add_params(hover))
    points = base.mark_point(size=50, filled=True, opacity=1).encode(
        y=f"{value}:Q").transform_filter(hover)
    return (lines + rule + points).properties(height=380).configure_view(strokeWidth=0)


def verdict(text: str, good: bool) -> str:
    colour, mark = (GOOD, "PASS") if good else (BAD, "FAIL")
    return (f"<span style='color:{colour};font-weight:600'>{'✔' if good else '✖'} {mark}</span>"
            f" &nbsp;{text}")


def run_test(symbols: list[str], settings: scoreboard.Settings, use_timesfm: bool,
             prices: pd.DataFrame) -> scoreboard.Result:
    forecasters = default_forecasters()
    if use_timesfm:
        forecasters.append(TimesFM(max_context=settings.max_context))
    slot = st.empty()          # cleared when the run ends
    box = slot.container(border=True)
    box.subheader("Test running")
    bar = box.progress(0.0, text="Starting ...")
    note = box.empty()
    live = box.empty()

    def progress(msg: str) -> None:
        note.caption(f"Working on {msg.strip()} (TimesFM is slow the first time; results are saved)")

    def on_symbol(done: int, total: int, rows: pd.DataFrame) -> None:
        bar.progress(done / total, text=f"{done} of {total} stocks done")
        if len(rows):
            table = rows.pivot(index="symbol", columns="strategy", values="cagr_pct")
            live.dataframe(table.drop(columns=CASH_RULE, errors="ignore").round(1),
                           use_container_width=True)
            note.caption("Return per year after costs (%), stock by stock as each finishes")

    result = scoreboard.run(prices, symbols, settings, forecasters,
                            cache_dir=config.FORECAST_CACHE_DIR, progress=progress,
                            on_symbol=on_symbol)
    slot.empty()
    return result


def show_summary(result: scoreboard.Result) -> None:
    trading = result.trading.set_index("strategy")
    hold = trading.loc["Buy and hold"]
    rules = trading[trading.index.str.startswith(("Forecast rule", "Moving-average"))]
    rules = rules.drop(index=CASH_RULE, errors="ignore")
    best = rules["cagr_pct"].idxmax()
    acc = result.accuracy.set_index("forecaster").drop(index="No change", errors="ignore")
    top = acc["skill_vs_no_change"].idxmax()

    a, b, c, d = st.columns(4)
    a.metric("Buy and hold, per year", f"{hold['cagr_pct']:.1f}%",
             help="After costs. This is the return any strategy has to beat.")
    b.metric("Best strategy, per year", f"{rules.loc[best, 'cagr_pct']:.1f}%",
             f"{rules.loc[best, 'cagr_pct'] - hold['cagr_pct']:+.1f} pts vs buy and hold", help=best)
    c.metric("Best forecast skill", f"{acc.loc[top, 'skill_vs_no_change']:+.3f}",
             help=f"{top}. Above zero means better than assuming the price stays put.")
    d.metric("Worst drop, buy and hold", f"{hold['max_drawdown_pct']:.1f}%")

    st.markdown("**Does anything pass?**")
    for name, row in acc.iterrows():
        ok = row["skill_vs_no_change"] > 0
        st.markdown(verdict(f"{name}: forecast skill {row['skill_vs_no_change']:+.4f}, "
                            f"beats no change on {row['symbols_beaten']} stocks", ok),
                    unsafe_allow_html=True)
    for name, row in rules.iterrows():
        ok = row["cagr_pct"] > hold["cagr_pct"]
        st.markdown(verdict(f"{name}: {row['cagr_pct']:.1f}% a year after costs "
                            f"against {hold['cagr_pct']:.1f}% for buy and hold", ok),
                    unsafe_allow_html=True)


def show_scoreboard(result: scoreboard.Result) -> None:
    st.markdown("##### Forecast accuracy")
    st.caption("Skill above zero means the forecaster beats assuming the price stays where it is.")
    acc = result.accuracy.rename(columns={
        "forecaster": "Forecaster", "forecasts": "Forecasts", "mae_pct": "Avg error (%)",
        "skill_vs_no_change": "Skill vs no change", "direction_hit_pct": "Direction right (%)",
        "symbols_beaten": "Stocks where it beats no change"}).drop(columns="rmse_pct")
    st.dataframe(acc.style.format({"Forecasts": "{:,.0f}", "Avg error (%)": "{:.3f}",
                                   "Skill vs no change": "{:+.4f}",
                                   "Direction right (%)": "{:.1f}"}, na_rep="n/a"),
                 hide_index=True, use_container_width=True)
    st.markdown("##### Skill by year")
    st.caption("A real edge shows up in most years, not just one.")
    by_year = result.skill_by_year[result.skill_by_year["forecaster"] != "No change"]
    years = [c for c in by_year.columns if c != "forecaster"]
    st.dataframe(by_year.rename(columns={"forecaster": "Forecaster"})
                 .style.format({y: "{:+.4f}" for y in years}),
                 hide_index=True, use_container_width=True)
    st.markdown("##### Trading results after costs")
    trade = result.trading.drop(columns="volatility_pct").rename(columns={
        "strategy": "Strategy", "total_return_pct": "Total return (%)", "cagr_pct": "Per year (%)",
        "max_drawdown_pct": "Worst drop (%)", "sharpe": "Sharpe", "trades": "Trades",
        "costs_rupees": "Costs (Rs)", "exposure_pct": "Time invested (%)"})
    st.dataframe(trade.style.format({
        "Total return (%)": "{:.1f}", "Per year (%)": "{:.1f}", "Worst drop (%)": "{:.1f}",
        "Sharpe": "{:.2f}", "Trades": "{:,.0f}", "Costs (Rs)": "{:,.0f}",
        "Time invested (%)": "{:.0f}"}, na_rep="n/a"), hide_index=True, use_container_width=True)
    st.caption("The index row pays no costs and leaves out dividends; the strategies pay "
               "full costs and include dividends.")


def show_growth(result: scoreboard.Result) -> None:
    names = [n for n in result.equity if n != CASH_RULE]
    shown = st.multiselect("Lines to show", names, default=names)
    if not shown:
        st.info("Pick at least one line.")
        return
    start = sum(result.equity[n].iloc[0] for n in shown[:1])
    frames = [pd.DataFrame({"date": result.equity[n].index, "series": n,
                            "value": result.equity[n].to_numpy() / 1e5}) for n in shown]
    df = pd.concat(frames, ignore_index=True)
    colours = {n: c for n, c in colour_map(names).items() if n in shown}
    st.caption(f"Value of Rs {start / 1e5:,.0f} lakh put in on {result.start:%d %b %Y}, after costs")
    st.altair_chart(line_chart(df, "value", "Rs lakh", ",.1f", colours,
                               dashed=(scoreboard.BENCHMARK_LABEL,)), use_container_width=True)
    with st.expander("Show as a table (month ends)"):
        wide = df.pivot(index="date", columns="series", values="value").resample("ME").last()
        st.dataframe(wide.round(2), use_container_width=True)


def show_forecasts(result: scoreboard.Result, horizon: int) -> None:
    a, b, c = st.columns([1, 1, 1])
    symbol = a.selectbox("Stock", result.symbols)
    choices = [f for f in result.forecasts if f != "No change"]
    default = next((i for i, f in enumerate(choices) if f.startswith("TimesFM")), 0)
    forecaster = b.selectbox("Forecaster", choices, index=default)
    days = c.select_slider("Show last", [60, 120, 250, 500, 1000, "All"], value=250,
                           format_func=lambda v: v if v == "All" else f"{v} days")
    frame = result.forecasts[forecaster][symbol]
    actual = frame["close"]
    # A forecast made on day t is for day t + horizon: draw it on the day it is for.
    forecast = pd.Series(frame["pred_price"].to_numpy()[:-horizon], index=frame.index[horizon:])
    if days != "All":
        actual, forecast = actual.iloc[-days:], forecast.iloc[-days:]
    df = pd.concat([
        pd.DataFrame({"date": actual.index, "series": "Actual close", "value": actual.to_numpy()}),
        pd.DataFrame({"date": forecast.index, "series": f"Forecast made {horizon} days earlier",
                      "value": forecast.to_numpy()})], ignore_index=True)
    colours = {"Actual close": SLOTS[0], f"Forecast made {horizon} days earlier": SLOTS[1]}
    st.altair_chart(line_chart(df, "value", "Price (Rs, adjusted)", ",.1f", colours,
                               axis_fmt=",.0f"),
                    use_container_width=True)
    scored = frame.dropna(subset=["actual_ret"])
    if days != "All":
        scored = scored.iloc[-days:]
    err = (scored["pred_ret"] - scored["actual_ret"]).abs().mean() * 100
    naive = scored["actual_ret"].abs().mean() * 100
    x, y, z = st.columns(3)
    x.metric("Avg error, this forecaster", f"{err:.2f}%")
    y.metric("Avg error, no change", f"{naive:.2f}%")
    z.metric("Skill vs no change", f"{1 - err / naive:+.3f}",
             help="Above zero means the forecaster was closer than assuming no change.")
    st.caption("If the forecast line just trails the actual line, the forecaster is "
               "repeating recent prices rather than predicting.")


def show_by_stock(result: scoreboard.Result) -> None:
    st.caption("Return per year after costs (%)")
    table = result.by_symbol.pivot(index="symbol", columns="strategy", values="cagr_pct")
    st.dataframe(table.drop(columns=CASH_RULE, errors="ignore").style.format("{:.1f}"),
                 use_container_width=True)
    st.markdown("##### Costs paid (Rs)")
    cost = result.by_symbol.pivot(index="symbol", columns="strategy", values="costs_rupees")
    st.dataframe(cost.drop(columns=CASH_RULE, errors="ignore").style.format("{:,.0f}"),
                 use_container_width=True)


def show_data_checks(result: scoreboard.Result) -> None:
    if not config.ACTIONS_PATH.exists():
        st.info("No corporate-actions file yet. Run `python -m silkperfect build`.")
        return
    events = pd.read_csv(config.ACTIONS_PATH, parse_dates=["ex_date"])
    mine = events[events["symbol"].isin(result.symbols) & (events["kind"] != "other")]
    review = mine[mine["status"].isin(("unconfirmed", "unparsed"))]
    a, b, c = st.columns(3)
    a.metric("Dividends applied", int(((mine["kind"] == "dividend") & (mine["status"] == "applied")).sum()))
    b.metric("Splits, bonuses, demergers applied",
             int((mine["status"].isin(("applied", "estimated", "manual"))
                  & (mine["kind"] != "dividend")).sum()))
    c.metric("Need a manual look", len(review))
    if len(review):
        st.markdown("##### Not adjusted: add to `config/corporate_actions_manual.csv` if they matter")
        st.dataframe(review[["symbol", "ex_date", "purpose", "status"]], hide_index=True,
                     use_container_width=True)
    st.markdown("##### Splits, bonuses and demergers applied")
    big = mine[(mine["kind"] != "dividend") & mine["status"].isin(("applied", "estimated", "manual"))]
    st.dataframe(big[["symbol", "ex_date", "purpose", "factor", "status"]], hide_index=True,
                 use_container_width=True)


def page_stock_test() -> None:
    st.title("Single-share forecast test")

    if not config.PRICES_PATH.exists():
        st.error("No price data yet. In a terminal run:  python -m silkperfect run")
        st.stop()
    stamp = config.PRICES_PATH.stat().st_mtime
    st.caption(f"NSE prices up to {last_data_day(stamp):%d %b %Y}. To add newer days run "
               "`python -m silkperfect fetch` then `python -m silkperfect build`.")

    universe = config.load_universe()
    with st.sidebar:
        st.header("Test settings")
        with st.form("settings"):
            symbols = st.multiselect("Stocks", all_symbols(stamp), default=universe)
            horizon = st.slider("Forecast horizon (trading days)", 1, 20, config.HORIZON)
            capital = st.number_input("Money per stock (Rs)", 50_000, 50_000_000,
                                      int(config.CAPITAL_PER_SYMBOL), step=50_000)
            have = timesfm_installed()
            use_timesfm = st.checkbox(
                "Include TimesFM 2.5", value=False, disabled=not have,
                help="About 2 to 3 minutes per stock the first time; saved after that."
                if have else "Not installed. Run: pip install -r requirements-timesfm.txt")
            pressed = st.form_submit_button("Run test", type="primary", use_container_width=True)
        st.caption("Results are a test on past prices. They do not predict future returns.")

    if not symbols:
        st.info("Pick at least one stock on the left.")
        st.stop()

    wanted = (tuple(symbols), horizon, capital, use_timesfm, stamp)
    if pressed or "result" not in st.session_state:
        settings = scoreboard.Settings(horizon=horizon, capital=float(capital))
        prices = load_prices(tuple(sorted(set(symbols) | {settings.benchmark})), stamp)
        try:
            st.session_state["result"] = run_test(symbols, settings, use_timesfm, prices)
        except ValueError as exc:
            st.error(f"Could not run: {exc}")
            st.stop()
        st.session_state["ran_with"] = wanted
        st.session_state["finished"] = pd.Timestamp.now()
    result: scoreboard.Result = st.session_state["result"]
    ran_symbols, ran_horizon, ran_capital, ran_timesfm, _ = st.session_state["ran_with"]

    st.markdown(f"**{len(result.symbols)} stocks**, {result.start:%d %b %Y} to "
                f"{result.end:%d %b %Y}, {ran_horizon}-day forecasts, Rs {ran_capital:,.0f} per stock. "
                f"Last run {st.session_state['finished']:%H:%M:%S}.")
    if result.skipped:
        st.warning("Skipped for too little price history: " + ", ".join(result.skipped))

    show_summary(result)
    tabs = st.tabs(["Growth of money", "Forecast vs actual", "Scoreboard", "By stock", "Data checks"])
    with tabs[0]:
        show_growth(result)
    with tabs[1]:
        show_forecasts(result, ran_horizon)
    with tabs[2]:
        show_scoreboard(result)
    with tabs[3]:
        show_by_stock(result)
    with tabs[4]:
        show_data_checks(result)


# ---- Simple view ---------------------------------------------------------------

SWAP_CHOICES = {"Every month": 21, "Every 3 months": 63, "Every 6 months": 126}


def rupees(value: float) -> str:
    return f"Rs {value:,.0f}"


@st.cache_resource(show_spinner="Loading share prices ...")
def load_market(stamp: float):
    prices = dataset.load_prices()
    return prices, ranking.make_panel(prices, exclude=ranking.etf_symbols())


@st.cache_resource(show_spinner="Working it out ...")
def plan_outcome(amount: float, method: str, held: int, swap: int, start: str | None, stamp: float):
    prices, panel = load_market(stamp)
    plan = paper.Plan(amount=amount, method=method, shares_held=held, swap_every_days=swap)
    return paper.run_plan(panel, prices, plan, start=pd.Timestamp(start) if start else None,
                          cache_dir=config.FORECAST_CACHE_DIR)


def method_choices() -> dict[str, str]:
    choices = dict(paper.METHODS)
    if not timesfm_installed():
        choices.pop("timesfm")
    if importlib.util.find_spec("chronos") is None:
        choices.pop("chronos", None)
    return choices


def growth_chart(o: paper.Outcome, with_everything: bool = True) -> None:
    lines = {"This plan": o.equity, "One Nifty 50 fund, bought once": o.fund,
             f"Bank deposit at {paper.BANK_RATE:.1%} a year": o.bank}
    if with_everything:
        lines["All 200 big shares (comparison only)"] = o.everything
    colours = dict(zip(lines, [SLOTS[0], SLOTS[1], SLOTS[2], BENCHMARK_COLOUR]))
    df = pd.concat([pd.DataFrame({"date": v.index, "series": k, "value": v.to_numpy()})
                    for k, v in lines.items()], ignore_index=True)
    st.altair_chart(line_chart(df, "value", "Rupees", ",.0f", colours,
                               dashed=("All 200 big shares (comparison only)",)),
                    use_container_width=True)


def show_looking_back(o: paper.Outcome) -> None:
    plan, fund, bank = o.equity.iloc[-1], o.fund.iloc[-1], o.bank.iloc[-1]
    st.subheader(f"If you had started on {o.start:%d %B %Y}")
    a, b, c, d = st.columns(4)
    a.metric("This plan would be worth", rupees(plan), f"{plan - o.plan.amount:+,.0f} rupees")
    b.metric("One Nifty 50 fund instead", rupees(fund), f"{fund - o.plan.amount:+,.0f} rupees")
    c.metric("Bank deposit instead", rupees(bank), f"{bank - o.plan.amount:+,.0f} rupees")
    d.metric("Fees this plan paid", rupees(o.fees), help="Brokerage, taxes and charges on every "
             "buy and sell. They are already taken out of the first number.")

    # Stated plainly, without a pass mark: one setting doing well on old prices proves little.
    if plan > fund:
        st.markdown(f"On past prices this plan ended **{rupees(plan - fund)} ahead** of simply "
                    "buying one Nifty 50 fund. Read the three notes under the chart before trusting that.")
    else:
        st.markdown(f"On past prices this plan ended **{rupees(fund - plan)} behind** simply "
                    "buying one Nifty 50 fund. The simple fund did better with no work.")
    growth_chart(o)

    peak, low, pct = o.worst_fall
    st.markdown(f"**The hard part.** At its worst, this plan fell from {rupees(peak)} to "
                f"{rupees(low)}, a drop of {abs(pct):.0f}%. A plan only works if you can sit "
                "through a fall like that without selling.")
    share_of_fees = o.fees / o.plan.amount * 100
    if share_of_fees > 50:
        st.markdown(f"**Fees are heavy at this size.** The plan paid {rupees(o.fees)} in fees on "
                    f"{rupees(o.plan.amount)} put in ({share_of_fees:.0f}%). Each buy or sell costs "
                    "roughly Rs 20 to Rs 45 however small it is, so swapping shares less often, "
                    "or putting in more money, changes the result a lot.")
    if pd.isna(o.rank_t_stat):
        luck = "There is too little history to say whether this is skill or luck."
    elif o.rank_t_stat >= 2:
        luck = "The picking method shows a pattern that is unlikely to be luck alone."
    else:
        luck = ("The picking method's edge is weak enough that luck cannot be ruled out. "
                "Try other settings above: if the answer swings a lot, do not trust any one of them.")
    st.markdown(f"**Skill or luck?** {luck}")


def show_pretend_account(stamp: float, amount: float, method: str, held: int, swap: int,
                         last_day: pd.Timestamp) -> None:
    st.subheader("Pretend account")
    st.caption("No real money. The computer follows the plan with pretend rupees and real "
               "share prices, so you can watch how it does from today onward.")
    account = paper.load_account()
    if account is None:
        st.write(f"No pretend account yet. Starting one puts a pretend {rupees(amount)} into the "
                 "plan chosen above, beginning with the latest share prices.")
        if st.button(f"Start a pretend account with {rupees(amount)}", type="primary"):
            paper.start_account(paper.Plan(amount=amount, method=method, shares_held=held,
                                           swap_every_days=swap), last_day)
            st.rerun()
        return

    plan = account["plan"]
    o = plan_outcome(plan.amount, plan.method, plan.shares_held, plan.swap_every_days,
                     f"{account['start']:%Y-%m-%d}", stamp)
    now = o.equity.iloc[-1]
    swap_words = next((k for k, v in SWAP_CHOICES.items() if v == plan.swap_every_days),
                      f"every {plan.swap_every_days} trading days").lower()
    st.write(f"Started **{account['start']:%d %B %Y}** with **{rupees(plan.amount)}**. "
             f"Plan: hold {plan.shares_held} shares, picked as "
             f"\"{paper.METHODS[plan.method].lower()}\", swapped {swap_words}.")
    a, b, c, d = st.columns(4)
    a.metric("Worth today", rupees(now), f"{now - plan.amount:+,.0f} rupees")
    b.metric("Fees paid so far", rupees(o.fees))
    c.metric("Cash not invested", rupees(o.cash if len(o.trades) else plan.amount))
    d.metric("Market days until next swap", f"{max(o.days_to_next_swap, 0)}")

    if o.picks_waiting and not len(o.trades):
        st.info("Shares chosen, to be bought when the market next opens (after you next "
                "update prices): " + ", ".join(o.picks_waiting))
    elif o.picks_waiting:
        st.info("New picks waiting for the next market open: " + ", ".join(o.picks_waiting))
    if len(o.holdings):
        st.markdown("**What the account holds now**")
        st.dataframe(o.holdings.style.format({"Price now (Rs)": "{:,.2f}", "Worth now (Rs)": "{:,.0f}",
                                              "Last bought at (Rs)": "{:,.2f}"}),
                     hide_index=True, use_container_width=True)
    if len(o.equity) > 5:
        growth_chart(o, with_everything=False)
    if len(o.trades):
        st.markdown("**Every buy and sell so far**")
        log = o.trades.sort_values("date", ascending=False).rename(columns={
            "date": "Date", "symbol": "Share", "action": "What", "shares": "How many",
            "price": "Price (Rs)", "fees": "Fees (Rs)"})
        st.dataframe(log.style.format({"Date": "{:%d %b %Y}", "How many": "{:.0f}",
                                       "Price (Rs)": "{:,.2f}", "Fees (Rs)": "{:,.2f}"}),
                     hide_index=True, use_container_width=True)
    with st.expander("Close this pretend account"):
        st.write("This forgets the account. You can start a new one afterwards.")
        if st.button("Yes, close it"):
            paper.close_account()
            st.rerun()


def page_simple() -> None:
    st.title("What happens to your money?")
    if not config.PRICES_PATH.exists():
        st.error("No price data yet. In a terminal run:  python -m silkperfect dashboard")
        st.stop()
    stamp = config.PRICES_PATH.stat().st_mtime
    last_day = last_data_day(stamp)
    st.caption(f"Uses real NSE share prices up to {last_day:%d %B %Y}. Nothing here places a real order.")

    choices = method_choices()
    a, b, c, d = st.columns(4)
    amount = a.number_input("Money to put in (Rs)", 1_000, 100_000_000, 10_000, step=1_000)
    method = b.selectbox("How shares are picked", list(choices), format_func=choices.get)
    held = c.selectbox("How many shares to hold", [3, 5, 10, 20], index=1)
    swap_label = d.selectbox("How often to swap them", list(SWAP_CHOICES), index=1)
    swap = SWAP_CHOICES[swap_label]
    st.caption("The plan: from the 200 most traded shares on NSE, buy the best few by the chosen "
               "method, in equal amounts, and swap them for the new best ones on the chosen schedule.")

    try:
        outcome = plan_outcome(float(amount), method, held, swap, None, stamp)
    except (ValueError, SystemExit) as exc:
        st.error(f"Could not work this plan out: {exc}")
        st.stop()
    show_looking_back(outcome)
    st.divider()
    show_pretend_account(stamp, float(amount), method, held, swap, last_day)
    st.divider()
    st.subheader("Things to know")
    st.markdown(
        "- **The past does not promise the future.** A plan that worked on old prices can fail from tomorrow.\n"
        "- **Small changes swing the result.** If changing the settings above flips a plan from good to bad, "
        "the good result was mostly luck.\n"
        "- **A pretend account needs months, not days,** before it says anything.\n"
        "- **Real-money trading is switched off.** This page only reads prices and does arithmetic.\n"
        "- This is a testing tool, not financial advice.")


def page_ranking() -> None:
    st.title("Pick-the-best test")
    path = config.REPORTS_DIR / "ranking_summary.csv"
    if not path.exists():
        st.info("No results yet. In a terminal run:  python -m silkperfect rank")
        return
    st.caption("From the 200 most traded NSE shares, each method buys its top 20 every month with "
               "Rs 1 crore. The bar to beat is holding all 200 equally. Refresh these numbers with "
               "`python -m silkperfect rank --models`.")
    summary = pd.read_csv(path)
    base = summary.set_index("method").loc[ranking.HOLD_ALL, "cagr_pct"]
    for _, r in summary[summary["method"] != ranking.HOLD_ALL].iterrows():
        strong = r["rank_t_stat"] >= 2
        beat = r["cagr_pct"] > base
        text = (f"{r['method']}: {r['cagr_pct']:.1f}% a year against {base:.1f}% for holding all 200; "
                + ("pattern unlikely to be luck" if strong else "luck not ruled out")
                + f" (strength {r['rank_t_stat']:+.2f}, needs 2 or more)")
        st.markdown(verdict(text, bool(beat and strong)), unsafe_allow_html=True)
    equity = pd.read_csv(config.REPORTS_DIR / "ranking_equity.csv", index_col="date", parse_dates=True)
    names = list(equity.columns)
    palette = [BENCHMARK_COLOUR] + SLOTS
    colours = {n: palette[i] for i, n in enumerate(names)}
    df = (equity / 1e5).reset_index().melt("date", var_name="series", value_name="value").dropna()
    st.caption("Value of Rs 1 crore, after costs, in Rs lakh")
    st.altair_chart(line_chart(df, "value", "Rs lakh", ",.0f", colours, dashed=(ranking.HOLD_ALL,)),
                    use_container_width=True)
    table = summary.rename(columns={
        "method": "Method", "cagr_pct": "Per year (%)", "max_drawdown_pct": "Worst drop (%)",
        "sharpe": "Sharpe", "turnover_pct": "Swapped each month (%)", "costs_rupees": "Costs (Rs)",
        "cagr_before_pct": "Per year before last 12 months (%)",
        "return_holdout_pct": "Last 12 months (%)", "rank_correlation": "Rank correlation",
        "rank_t_stat": "Strength (t)", "periods_won_pct": "Months it beat hold-all (%)"})
    st.dataframe(table.style.format({
        "Per year (%)": "{:.1f}", "Worst drop (%)": "{:.1f}", "Sharpe": "{:.2f}",
        "Swapped each month (%)": "{:.0f}", "Costs (Rs)": "{:,.0f}",
        "Per year before last 12 months (%)": "{:.1f}", "Last 12 months (%)": "{:.1f}",
        "Rank correlation": "{:+.3f}", "Strength (t)": "{:+.2f}",
        "Months it beat hold-all (%)": "{:.0f}"}, na_rep="n/a"),
        hide_index=True, use_container_width=True)


PAGES = {"Simple view": page_simple, "Pick-the-best test": page_ranking,
         "Single-share forecast test": page_stock_test}


def main() -> None:
    st.set_page_config(page_title="Silkperfect", page_icon="📈", layout="wide")
    with st.sidebar:
        page = st.radio("Page", list(PAGES))
        st.divider()
    PAGES[page]()


main()
