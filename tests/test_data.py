from datetime import date

import pandas as pd
import pytest

from silkperfect import corporate_actions as ca, dataset, nse, parse
from conftest import make_zip


def test_pr_bundle_parses_stocks_index_and_actions(pr_zip):
    path = pr_zip(date(2024, 1, 4), [("NESTLEIND", 26635.20, 26851.05, 27150.05, 26652.05, 27116.40)],
                  actions=[("NESTLEIND", "05/01/2024", "FVSPLT FRM RS 10 TO RE 1")])
    prices, actions = parse.parse_pr_zip(path)
    assert set(prices["symbol"]) == {"NESTLEIND", "NIFTY 50"}     # bond row dropped
    row = prices.set_index("symbol").loc["NESTLEIND"]
    assert (row["close"], row["prev_close"], row["series"]) == (27116.40, 26635.20, "EQ")
    assert prices.set_index("symbol").loc["NIFTY 50", "series"] == "INDEX"
    assert actions.iloc[0]["ex_date"] == pd.Timestamp("2024-01-05")
    assert actions.iloc[0]["seen"] == pd.Timestamp("2024-01-04")


def test_new_style_member_names_are_found(pr_zip):
    path = pr_zip(date(2026, 11, 9), [("ABC", 10, 10, 11, 9, 10.5)], lower=True)
    prices, _ = parse.parse_pr_zip(path)
    assert "ABC" in set(prices["symbol"])


def test_legacy_and_udiff_bhavcopy_agree(tmp_path):
    legacy = tmp_path / "l.zip"
    legacy.write_bytes(make_zip({"cm05JAN2024bhav.csv":
        "SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN,\n"
        "NESTLEIND,EQ,2754.0,2754.0,2642.45,2666.4,2668.1,27116.4,2577064,6884888559.9,05-JAN-2024,193592,INE239A01024,\n"}))
    udiff = tmp_path / "u.zip"
    udiff.write_bytes(make_zip({"BhavCopy_NSE_CM_0_0_0_20240105_F_0000.csv":
        "TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,OpnPric,HghPric,LwPric,ClsPric,"
        "LastPric,PrvsClsgPric,TtlTradgVol,TtlTrfVal,TtlNbOfTxsExctd\n"
        "2024-01-05,2024-01-05,CM,NSE,STK,17963,INE239A01024,NESTLEIND,EQ,2754.0,2754.0,2642.45,2666.4,"
        "2668.1,27116.4,2577064,6884888559.9,193592\n"}))
    a, b = parse.parse_legacy_bhavcopy(legacy), parse.parse_udiff_bhavcopy(udiff)
    assert list(a.columns) == parse.PRICE_COLUMNS == list(b.columns)
    pd.testing.assert_frame_equal(a, b)


def test_symbol_changes_follow_chains(tmp_path):
    f = tmp_path / "s.csv"
    f.write_text("NAME OF THE COMPANY,OLD SYMBOL,NEW SYMBOL,EFFECTIVE DATE\n"
                 "A Ltd,AAA,BBB,01-JAN-2020\nA Ltd,BBB,CCC,01-JAN-2022\nBad,X,Y,28-MAR-\n")
    assert parse.parse_symbol_changes(f) == {"AAA": "CCC", "BBB": "CCC"}


@pytest.mark.parametrize("text,kind,value", [
    ("FVSPLT FRM RS 10 TO RE 1", "split", 0.1),
    ("FV SPLT FRM RS 10 TO RS 5", "split", 0.5),
    ("FVSPLT FRM RS# TO RS #".replace("#", "2", 1).replace("#", "1"), "split", 0.5),
    ("BONUS 1:1", "bonus", 0.5),
    ("BONUS 2:1", "bonus", 1 / 3),
    ("INTDIV - RS 5 PER SH", "dividend", 5.0),
    ("AGM/DIV - RE 0.50 PER SH", "dividend", 0.5),
    ("SPLDIV-3/INTDIV-2", "dividend", 5.0),
    ("2ND INT DIV - RS 4 PER SH", "dividend", 4.0),
    ("INTERIM DIVIDEND", "dividend", None),
    ("RIGHTS 1:14 @PRM RS 530", "unhandled", None),
    ("DEMERGER", "demerger", None),
    ("ANNUAL GENERAL MEETING", "other", None),
])
def test_parse_purpose(text, kind, value):
    act = ca.parse_purpose(text)[0]
    assert act.kind == kind
    got = act.ratio if kind in ("split", "bonus") else act.amount
    assert got == pytest.approx(value) if value is not None else got is None


def test_combined_bonus_and_split_text():
    kinds = {a.kind: a.ratio for a in ca.parse_purpose("BON1:1/FVSPLTFRMRS5TORS2")}
    assert kinds == {"split": pytest.approx(0.4), "bonus": pytest.approx(0.5)}


def _prices(rows):
    return pd.DataFrame(rows, columns=["date", "symbol", "open", "close"]).assign(
        date=lambda d: pd.to_datetime(d["date"]), high=lambda d: d["open"],
        low=lambda d: d["close"], volume=100.0)


def _actions(rows):
    df = pd.DataFrame(rows, columns=["symbol", "ex_date", "purpose", "seen"])
    return df.assign(ex_date=pd.to_datetime(df["ex_date"]), seen=pd.to_datetime(df["seen"]))


PX = _prices([("2024-01-03", "S", 1000, 1000), ("2024-01-04", "S", 1000, 1000),
              ("2024-01-05", "S", 101, 100), ("2024-01-08", "S", 100, 102)])


def test_split_confirmed_by_price_makes_series_continuous():
    events = ca.build_events(_actions([("S", "2024-01-05", "FVSPLT FRM RS 10 TO RE 1", "2024-01-04")]), PX)
    assert events.iloc[0]["status"] == "applied"
    adj = ca.adjust_prices(PX, events)
    assert list(adj["adj_close"]) == pytest.approx([100, 100, 100, 102])
    assert list(adj["adj_volume"]) == pytest.approx([1000, 1000, 100, 100])
    assert len(ca.unexplained_gaps(adj)) == 0
    assert len(ca.unexplained_gaps(ca.adjust_prices(PX, events.iloc[0:0]))) == 1


def test_split_not_seen_in_prices_is_left_alone():
    events = ca.build_events(_actions([("S", "2024-01-08", "FVSPLT FRM RS 10 TO RE 1", "2024-01-05")]), PX)
    assert events.iloc[0]["status"] == "unconfirmed" and events.iloc[0]["factor"] == 1.0


def test_same_action_listed_twice_is_applied_once():
    events = ca.build_events(_actions([
        ("S", "2024-01-05", "FVSPLT FRM RS 10 TO RE 1", "2024-01-04"),
        ("S", "2024-01-05", "FV SPLT FRM RS 10 TO RE 1", "2024-01-04")]), PX)
    assert sorted(events["status"]) == ["applied", "duplicate"]
    assert ca.adjust_prices(PX, events)["adj_factor"].iloc[0] == pytest.approx(0.1)


def test_dividend_uses_last_listing_and_drops_revised_dates():
    events = ca.build_events(_actions([
        ("S", "2024-01-04", "INTERIM DIVIDEND", "2024-01-02"),          # early, no amount
        ("S", "2024-01-04", "INTDIV - RS 20 PER SH", "2024-01-03"),      # final wording
        ("S", "2024-01-08", "DIV - RS 5 PER SH", "2023-12-20"),          # date later revised
    ]), PX)
    by_date = events.set_index("ex_date")
    assert len(by_date.loc["2024-01-04":"2024-01-04"]) == 1
    assert by_date.loc["2024-01-04", "factor"] == pytest.approx(0.98)
    assert by_date.loc["2024-01-08", "status"] == "superseded"


def test_manual_override_replaces_detected_events():
    manual = pd.DataFrame({"symbol": ["S"], "ex_date": ["2024-01-05"], "factor": [0.25], "note": ["x"]})
    events = ca.build_events(_actions([("S", "2024-01-05", "FVSPLT FRM RS 10 TO RE 1", "2024-01-04")]),
                             PX, manual)
    assert list(events["status"]) == ["manual"] and events.iloc[0]["factor"] == 0.25


def test_build_end_to_end_with_rename(pr_zip, tmp_path):
    pr_zip(date(2024, 1, 4), [("OLD", 1000, 1000, 1000, 1000, 1000)],
           actions=[("OLD", "05/01/2024", "BONUS 1:1")])
    pr_zip(date(2024, 1, 5), [("NEW", 1000, 505, 510, 495, 500)])
    prices, events = dataset.build(tmp_path / "pr", renames={"OLD": "NEW"})
    bars = dataset.ohlcv(prices, "NEW")
    assert list(bars["Close"]) == pytest.approx([500, 500])
    assert events.iloc[0]["status"] == "applied"
    assert len(dataset.ohlcv(prices, "NIFTY 50")) == 2


def test_fetch_records_checksums_and_remembers_missing_days(tmp_path, monkeypatch):
    calls = []
    good = make_zip({"Pd010124.csv": "x"})

    def fake_get(url, tries=4):
        calls.append(url)
        return (200, good) if "PR010124" in url else (404, b"<html>")

    monkeypatch.setattr(nse, "http_get", fake_get)
    kw = dict(pr_dir=tmp_path / "pr", manifest_path=tmp_path / "m.csv", workers=1,
              today=date(2024, 6, 1))
    counts = nse.fetch_range(date(2024, 1, 1), date(2024, 1, 3), **kw)
    assert (counts["ok"], counts["missing"]) == (1, 2)
    assert nse.verify_manifest(tmp_path / "pr", tmp_path / "m.csv") == []
    assert nse.fetch_range(date(2024, 1, 1), date(2024, 1, 3), **kw)["skipped"] == 3
    assert len(calls) == 3                                   # nothing asked for twice
    nse.pr_path(date(2024, 1, 1), tmp_path / "pr").write_bytes(b"tampered")
    assert nse.verify_manifest(tmp_path / "pr", tmp_path / "m.csv") == ["2024-01-01"]
