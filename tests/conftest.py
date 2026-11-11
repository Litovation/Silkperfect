import io
import zipfile

import pytest

PD_HEADER = ("MKT,SERIES,SYMBOL,SECURITY,PREV_CL_PR,OPEN_PRICE,HIGH_PRICE,LOW_PRICE,"
             "CLOSE_PRICE,NET_TRDVAL,NET_TRDQTY,IND_SEC,CORP_IND,TRADES,HI_52_WK,LO_52_WK")
BC_HEADER = "SERIES,SYMBOL,SECURITY,RECORD_DT,BC_STRT_DT,BC_END_DT,EX_DT,ND_STRT_DT,ND_END_DT,PURPOSE"


def make_zip(members: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in members.items():
            z.writestr(name, text)
    return buf.getvalue()


@pytest.fixture
def pr_zip(tmp_path):
    """Write a PR bundle. rows are (symbol, prev, open, high, low, close) tuples."""
    def write(day, rows, actions=(), lower=False):
        pd_lines = [PD_HEADER,
                    "Y, , ,Nifty 50,     100.00,     101.00,     102.00,     99.00,     101.50,0,0,Y, ,0,.00,.00",
                    "N,GS,GSEC,Some bond, 1, 1, 1, 1, 1,1,1,N, ,1,1,1"]
        for sym, prev, o, h, l, c in rows:
            pd_lines.append(f"N,EQ,{sym},{sym} LTD,     {prev:.2f},     {o:.2f},     {h:.2f},"
                            f"     {l:.2f},     {c:.2f},   1000000.00,1000,Y, ,50,1,1")
        bc_lines = [BC_HEADER] + [
            f"EQ,{sym},{sym} LTD,{ex}, , ,{ex}, , ,{purpose:<25}" for sym, ex, purpose in actions]
        stamp = f"{day:%d%m%Y}" if lower else f"{day:%d%m%y}"
        pd_name = f"pd{stamp}.csv" if lower else f"Pd{stamp}.csv"
        bc_name = f"bc{stamp}.csv" if lower else f"Bc{stamp}.csv"
        folder = tmp_path / "pr" / f"{day:%Y}"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"PR{day:%d%m%y}.zip"
        path.write_bytes(make_zip({pd_name: "\n".join(pd_lines), bc_name: "\n".join(bc_lines),
                                   "Readme.txt": "x"}))
        return path
    return write
