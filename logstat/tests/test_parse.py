import pytest

from logstat.parser import parse_line

GOOD = '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245'

CASES = [
    pytest.param(GOOD, 200, id="valid"),
    pytest.param(GOOD.replace("6245", "-"), 200, id="dash-bytes"),
    pytest.param(GOOD.replace("-0400", "+0530"), 200, id="other-timezone"),
    pytest.param("", None, id="empty-line"),
    pytest.param(GOOD.replace("200 6245", "200"), None, id="missing-bytes"),
    pytest.param(GOOD.replace("Jul", "Jxl"), None, id="bad-month"),
    pytest.param(GOOD.replace("01/Jul", "32/Jul"), None, id="day-32"),
    pytest.param(GOOD.replace("GET", "get"), None, id="lowercase-method"),
    pytest.param(GOOD.replace("HTTP/1.0", '"HTTP/1.0'), None, id="stray-quote"),
    pytest.param(GOOD.replace("200 6245", "2000 6245"), None, id="four-digit-status"),
]


@pytest.mark.parametrize("line, status", CASES)
def test_parse_line(line: str, status: int | None) -> None:
    record = parse_line(line)
    if status is None:
        assert record is None
    else:
        assert record is not None
        assert record.status == status