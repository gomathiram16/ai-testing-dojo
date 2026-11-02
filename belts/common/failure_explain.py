"""Turn a pytest failure into one plain-English sentence.

Shared by the Black Belt agent (dojo_agent.py) and the injection round
(injection_live.py). Works the same for mock and live-AI tests, because it reads
the actual failure from pytest, not a pre-written answer.

Edit the WHY_* strings to re-word the explanations. Keep the {tokens}.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMISE THE WORDING HERE
# ─────────────────────────────────────────────────────────────────────────────
WHY_ACCEPTED   = ("Sent {request} and expected it to be rejected ({exp}), but DojoShop accepted it "
                  "({got}). Bad input was let through: likely a real DojoShop bug.")
WHY_NEGATIVE   = ("The total went negative ({value} cents){after}. Money should never go below zero: "
                  "likely a real DojoShop bug.")
WHY_TOTAL_SUM  = ("The total ({got} cents) doesn't match the sum of the items ({exp} cents){after}. "
                  "The total wasn't kept in step: likely a real DojoShop bug.")
WHY_BAD_OK     = ("Sent {request} and expected an error ({exp}), but DojoShop said OK ({got}). "
                  "Bad input was accepted: likely a real DojoShop bug.")
WHY_NOT_FOUND  = ("Sent {request} and expected OK ({exp}), but got 404 Not Found. That address may "
                  "not exist: likely a mistake in the AI's test (wrong URL).")
WHY_REJECTED   = ("Sent {request} and expected OK ({exp}), but DojoShop rejected it ({got}). Check "
                  "whether the test sent valid input.")
WHY_STATUS     = "Sent {request} and expected status {exp}, but got {got}."
WHY_NULL       = ("DojoShop returned an empty response (null) for {request}, where the test expected "
                  "data. A missing item should be a 'not found' error: that's a real DojoShop bug.")
WHY_FIELD      = ("The test read a field called '{field}', but DojoShop's response has no such "
                  "field: a mistake in the AI's test.")
WHY_COUNT      = ("Expected {exp} item(s), but got {got}: the AI guessed wrong about the data, or "
                  "the data changed.")
WHY_TOTAL      = ("{lead}the total was {got} cents, but the test expected {exp} cents. Check the "
                  "AI's maths first; if it's right, the total wasn't updated: likely a real DojoShop bug.")
WHY_VALUE      = "Expected {exp}, but DojoShop returned {got}."
WHY_CRASH      = "The test code itself crashed ({detail}): a mistake in the AI's test."
WHY_OTHER      = "pytest says: {detail}"
WHY_FOOTER     = ("Every failure is a candidate, not a verdict: decide whether it's a real DojoShop "
                  "bug or a mistake in the AI's test.")

_REQ = re.compile(
    r"(?:(\w+)\s*=\s*)?client\.(get|post|put|patch|delete)\(\s*[fr]?([\"'])(.+?)\3"
    r"(?:\s*,\s*json\s*=\s*(\{[^}]*\}))?", re.S)


def _requests(body: str) -> list[dict]:
    return [{"var": m.group(1), "method": m.group(2).upper(), "path": m.group(4),
             "json": m.group(5), "pos": m.start()} for m in _REQ.finditer(body or "")]


def _describe(req: dict | None, body: str = "", param: str | None = None) -> str:
    if not req:
        return "the request"
    path = re.sub(r"\{[^}]+\}", "…", req["path"])          # /carts/{c}/items -> /carts/…/items
    payload = req["json"] or ""
    # A value taken from a loop variable, e.g. {'code': code}: show the values the loop tries.
    for key, var in re.findall(r"['\"](\w+)['\"]\s*:\s*([A-Za-z_]\w*)\s*[,}]", payload):
        if param is not None:                      # parametrised test: name it from test_x[PCT101]
            q = '"' if '"' in payload else "'"
            payload = payload.replace(f": {var}", f": {q}{param}{q}")
            continue
        loop = re.search(rf"for\s+[^\n]*\b{var}\b[^\n]*\bin\s+\[(.*?)\]\s*:", body or "", re.S)
        if loop:
            values = re.findall(r"\(\s*(['\"][^'\"]+['\"])", loop.group(1)) or \
                     re.findall(r"(['\"][^'\"]+['\"])", loop.group(1))
            if values:
                payload = payload.replace(f": {var}", f": one of {', '.join(values)}")
    return f"{req['method']} {path}" + (f" {payload}" if payload else "")


def _request_for(body: str, source_line: str) -> dict | None:
    """The request the failing assertion is about: matched by variable, else the last one before it."""
    reqs = _requests(body)
    if not reqs:
        return None
    var = re.match(r"\s*assert\s+(?:not\s+)?\(?\s*(\w+)\.", source_line or "")
    if var:
        named = [r for r in reqs if r["var"] == var.group(1)]
        if named:
            return named[-1]
    pos = (body or "").find((source_line or "").strip()) if source_line else -1
    before = [r for r in reqs if pos < 0 or r["pos"] < pos]
    return (before or reqs)[-1]


def _lead(body: str) -> str:
    """Opening words for WHY_TOTAL, based on what the test did before checking the total."""
    if re.search(r"client\.delete\(", body or ""):
        return "After removing an item, "
    if re.search(r"/discount", body or ""):
        return "After applying a discount, "
    if re.search(r"client\.post\([^)]*/items", body or ""):
        return "After adding items, "
    return ""


def _after(body: str) -> str:
    if re.search(r"client\.delete\(", body or ""):
        return " after deleting an item"
    if re.search(r"/discount", body or ""):
        return " after applying a discount"
    return ""


def explain(body: str, message: str, text: str = "", name: str = "") -> str:
    """body = the test's source; message/text = pytest's failure message and traceback."""
    msg = message or ""
    first = msg.strip().splitlines()[0] if msg.strip() else "no details"
    first = re.sub(r"^AssertionError:\s*", "", first)
    src = ""
    m = re.search(r"in test_\w+\n(.*)", text or "")
    if m:
        src = m.group(1)
    req = _request_for(body, src)
    pm = re.search(r"\[(.+)\]$", name or "")
    request = _describe(req, body, pm.group(1) if pm else None)

    # Money went negative.
    neg = re.search(r"(-\d+)\s*>=?\s*0", first)
    if neg:
        return WHY_NEGATIVE.format(value=neg.group(1), after=_after(body))
    # Expected a rejection (status in (400, 422)) but it was accepted.
    if (st := re.match(r"assert (\d{3}) in \(([\d,\s]+)\)", first)):
        got, allowed = int(st.group(1)), [int(x) for x in re.findall(r"\d{3}", st.group(2))]
        if 200 <= got < 300 and all(400 <= a < 500 for a in allowed):
            return WHY_ACCEPTED.format(request=request, exp=" or ".join(map(str, allowed)), got=got)
    # Status code equality.
    if (st := re.match(r"assert (\d{3}) == (\d{3})\b", first)) and "status_code" in (msg + src):
        got, exp = int(st.group(1)), int(st.group(2))
        if 400 <= exp < 500 and 200 <= got < 300:
            return WHY_BAD_OK.format(request=request, exp=exp, got=got)
        if 200 <= exp < 300 and got == 404:
            return WHY_NOT_FOUND.format(request=request, exp=exp)
        if 200 <= exp < 300 and 400 <= got < 500:
            return WHY_REJECTED.format(request=request, exp=exp, got=got)
        return WHY_STATUS.format(request=request, exp=exp, got=got)
    # Total doesn't match the sum of line items.
    if (eq := re.match(r"assert (-?\d+) == (-?\d+)", first)) and "total" in src and "sum(" in src:
        return WHY_TOTAL_SUM.format(got=eq.group(1), exp=eq.group(2), after=_after(body))
    if "isinstance(None" in msg or "NoneType' object is not subscriptable" in msg:
        return WHY_NULL.format(request=request)
    if (k := re.match(r"KeyError: '([^']+)'", first)):
        return WHY_FIELD.format(field=k.group(1))
    if (c := re.match(r"assert (\d+) == (\d+)", first)) and ("len(" in msg or "len(" in src):
        return WHY_COUNT.format(exp=c.group(2), got=c.group(1))
    if (t := re.match(r"assert (-?\d+) == (-?\d+)\s*$", first)) and "total" in src.lower():
        lead = _lead(body)
        text = WHY_TOTAL.format(lead=lead, got=t.group(1), exp=t.group(2))
        return text if lead else text[0].upper() + text[1:]
    if (v := re.match(r"assert (.+?) == (.+)$", first)):
        return WHY_VALUE.format(exp=v.group(2), got=v.group(1))
    if re.match(r"\w+(Error|Exception)\b", first):
        return WHY_CRASH.format(detail=first[:80])
    return WHY_OTHER.format(detail=first[:100])


def read_junit(xml_path: str) -> list[tuple[str, str, str]]:
    """(test name, failure message, failure traceback) for every failed/errored test."""
    out = []
    try:
        for tc in ET.parse(xml_path).iter("testcase"):
            bad = tc.find("failure")
            if bad is None:
                bad = tc.find("error")
            if bad is not None:
                out.append((tc.get("name"), bad.get("message") or "", bad.text or ""))
    except (ET.ParseError, OSError):
        pass
    return out


class _Bodies(dict):
    """Test name -> source; 'test_x[PCT101]' (a parametrised run) finds 'test_x'."""
    def get(self, name, default=""):
        return super().get(name) or super().get((name or "").split("[")[0], default)


def test_bodies(code: str) -> dict[str, str]:
    """Map each test function name to its source (decorators included)."""
    return _Bodies({m.group(2): m.group(0) for m in re.finditer(
        r"^((?:@[^\n]*\n)*)def (test_\w+)\s*\(.*?(?=^@|^def |^class |\Z)", code or "", re.M | re.S)})
