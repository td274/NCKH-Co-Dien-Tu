#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kiem-tra-han-muc.py — Xem hạn mức (quota) của các API đã kết nối trong OpenCode.

Vì sao cần: mỗi nhà cung cấp tính hạn mức một kiểu khác nhau.
  - OpenCode Go : tính bằng TIỀN, có 3 mốc 5 giờ / tuần / tháng. Đọc được qua API.
  - Mistral     : không có endpoint quota; chỉ biết qua header rate-limit của
                  mỗi phản hồi (số request và số token mỗi phút).
  - Google      : không có endpoint quota công khai. Cách duy nhất là gửi một
                  request thật: 200 = còn, 429 = hết hạn mức.

Cách dùng:
  D:\\Python312\\python.exe kiem-tra-han-muc.py
  D:\\Python312\\python.exe kiem-tra-han-muc.py --json
  D:\\Python312\\python.exe kiem-tra-han-muc.py --chi-go

Lưu ý: script chỉ ĐỌC credential trong cơ sở dữ liệu cục bộ của OpenCode,
không in ra khóa, không gửi khóa đi đâu ngoài chính nhà cung cấp.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VN_TZ = timezone(timedelta(hours=7))
UA = "opencode-quota-check/1.0"


# --------------------------------------------------------------------------
# Đọc credential
# --------------------------------------------------------------------------
def _db_path() -> str:
    return os.path.expanduser(r"~\.local\share\opencode\opencode.db")


def _auth_json_paths() -> list[str]:
    home = os.path.expanduser("~")
    return [
        os.path.join(home, ".local", "share", "opencode", "auth.json"),
        os.path.join(home, ".config", "opencode", "auth.json"),
    ]


def read_credentials() -> dict[str, str]:
    """Trả về {integration_id: api_key}. Đọc DB trước, rồi tới auth.json."""
    creds: dict[str, str] = {}
    p = _db_path()
    if os.path.exists(p):
        try:
            con = sqlite3.connect("file:" + p.replace("\\", "/") + "?mode=ro", uri=True)
            for integ, value in con.execute("select integration_id, value from credential"):
                try:
                    obj = json.loads(value)
                    key = obj.get("key") or obj.get("apiKey") or obj.get("token")
                except (ValueError, TypeError):
                    key = value
                if key:
                    creds[integ] = key
            con.close()
        except sqlite3.Error as exc:
            print(f"  (không đọc được DB: {exc})", file=sys.stderr)

    for path in _auth_json_paths():
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for integ, obj in data.items():
            if integ in creds:
                continue
            if isinstance(obj, dict):
                key = obj.get("key") or obj.get("access") or obj.get("refresh")
            else:
                key = obj
            if isinstance(key, str) and key:
                creds[integ] = key
    return creds


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def http(url: str, key: str | None = None, payload: dict | None = None,
         timeout: int = 45) -> tuple[int | None, dict, dict, str]:
    """Trả về (status, headers, body_json, body_text). status=None nếu lỗi mạng."""
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"User-Agent": UA}
    if key:
        headers["Authorization"] = "Bearer " + key
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode("utf-8", "replace")
            try:
                body = json.loads(text)
            except ValueError:
                body = {}
            return r.status, dict(r.headers), body, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        try:
            body = json.loads(text)
        except ValueError:
            body = {}
        return e.code, dict(e.headers), body, text
    except Exception as e:  # noqa: BLE001 - báo lỗi mạng cho người dùng
        return None, {}, {}, f"{type(e).__name__}: {e}"


def vn_time(iso: str | None) -> str:
    if not iso:
        return "?"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    return dt.astimezone(VN_TZ).strftime("%H:%M %d/%m")


# --------------------------------------------------------------------------
# OpenCode Go
# --------------------------------------------------------------------------
def check_go(key: str) -> dict:
    status, _h, body, text = http("https://opencode.ai/inference/go/v1/usage", key)
    out: dict = {"provider": "OpenCode Go", "http": status}
    if status != 200:
        out["error"] = text[:300]
        return out

    meters = {}
    for name, label in (("rolling", "5 giờ"), ("weekly", "Tuần"), ("monthly", "Tháng")):
        m = (body.get("usage") or {}).get(name) or {}
        pct = m.get("percent")
        st = m.get("status")
        meters[label] = {
            "percent": pct,
            "status": st,
            "resets": vn_time(m.get("resetsAt")),
            "resets_iso": m.get("resetsAt"),
        }
    out["meters"] = meters

    # Hạn mức đô-la của từng model trong gói Go (để biết model nào "đắt hạn mức")
    st2, _h2, body2, _t2 = http("https://opencode.ai/inference/go/v1/models", key)
    if st2 == 200:
        rows = []
        for m in body2.get("data", []):
            go = (m.get("go") or {}).get("monthly_usage") or {}
            cost = ((m.get("cost") or {}).get("text") or {})
            rows.append({
                "id": m.get("id"),
                "allowance_usd": go.get("go"),
                "input": (cost.get("input") or {}).get("price"),
                "output": (cost.get("output") or {}).get("price"),
            })
        rows.sort(key=lambda r: (r["allowance_usd"] is None, r["allowance_usd"] or 0))
        out["models"] = rows
    return out


# --------------------------------------------------------------------------
# Mistral
# --------------------------------------------------------------------------
def check_mistral(key: str, model: str) -> dict:
    status, _h, body, text = http("https://api.mistral.ai/v1/models", key)
    out: dict = {"provider": "Mistral", "http": status, "test_model": model}
    if status != 200:
        out["error"] = text[:300]
        return out
    out["models"] = len(body.get("data", []))

    # Một request tối thiểu để lấy header rate-limit hiện tại.
    # Lưu ý: rate-limit phụ thuộc TỪNG model, nên đo bằng đúng model sẽ dùng.
    status2, headers, _b2, _t2 = http(
        "https://api.mistral.ai/v1/chat/completions", key,
        {"model": model,
         "messages": [{"role": "user", "content": "hi"}],
         "max_tokens": 1},
    )
    out["test_http"] = status2
    low = {k.lower(): v for k, v in headers.items()}
    rl = {k: low[k] for k in low if k.startswith("x-ratelimit")}
    out["rate_limit"] = rl
    if status2 == 429:
        out["error"] = "429 - đã chạm hạn mức tốc độ"
    return out


# --------------------------------------------------------------------------
# Google (Gemini)
# --------------------------------------------------------------------------
def check_google(key: str) -> dict:
    status, _h, body, text = http(
        "https://generativelanguage.googleapis.com/v1beta/models?key=" + key)
    out: dict = {"provider": "Google (Gemini)", "http": status}
    if status != 200:
        out["error"] = text[:300]
        return out
    out["models"] = len(body.get("models", []))

    # Không có endpoint quota -> gửi 1 token thật để dò 429/200.
    # Tên model thay đổi theo thời gian (model cũ bị gỡ với người dùng mới),
    # nên chọn động từ danh sách vừa lấy thay vì ghi cứng.
    candidates = []
    for m in body.get("models", []):
        name = (m.get("name") or "").split("/")[-1]
        if "generateContent" not in (m.get("supportedGenerationMethods") or []):
            continue
        if any(x in name for x in ("image", "tts", "transcribe", "embedding",
                                   "computer-use", "deep-research", "antigravity")):
            continue
        # Ưu tiên bản "latest" rồi tới số phiên bản cao nhất: model cũ có thể
        # vẫn nằm trong danh sách nhưng đã bị gỡ với người dùng mới (404).
        mver = re.search(r"gemini-(\d+(?:\.\d+)?)", name)
        version = float(mver.group(1)) if mver else 0.0
        tier = 2 if "lite" in name else 1 if "flash" in name else 0
        alias = 1 if name.endswith("-latest") else 0
        candidates.append((alias, version, tier, name))
    if not candidates:
        out["error"] = "không tìm được model text nào để thử"
        return out
    candidates.sort(reverse=True)
    test_model = candidates[0][3]
    out["test_model"] = test_model

    status2, _h2, body2, text2 = http(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + test_model + ":generateContent?key=" + key,
        payload={"contents": [{"parts": [{"text": "hi"}]}],
                 "generationConfig": {"maxOutputTokens": 1}},
    )
    out["test_http"] = status2
    if status2 == 429:
        out["error"] = "429 - hết hạn mức (free tier)"
    elif status2 and status2 != 200:
        out["error"] = text2[:200]
    return out


# --------------------------------------------------------------------------
# In kết quả
# --------------------------------------------------------------------------
def bar(pct: int | None) -> str:
    if pct is None:
        return "?"
    filled = min(20, max(0, round(pct / 5)))
    return "█" * filled + "·" * (20 - filled)


def print_go(r: dict) -> None:
    print("=" * 64)
    print("OPENCODE GO  (tính bằng tiền, không phải token)")
    print("=" * 64)
    if r.get("error"):
        print("  LỖI:", r["error"])
        return
    for label, m in (r.get("meters") or {}).items():
        pct = m.get("percent")
        flag = "  ← ĐANG CHẶN" if m.get("status") == "rate-limited" else ""
        print(f"  {label:7s} {bar(pct)} {pct:3d}%   reset {m['resets']} (giờ VN){flag}")
    models = r.get("models") or []
    if models:
        print("\n  Hạn mức tháng của từng model trong gói Go:")
        print(f"    {'model':24s} {'hạn mức $':>10s} {'vào/ra $ per 1M':>18s}")
        for m in models:
            if m["allowance_usd"] is None:
                continue
            print(f"    {m['id']:24s} {m['allowance_usd']:10.0f} "
                  f"{str(m['input']) + ' / ' + str(m['output']):>18s}")


def print_mistral(r: dict) -> None:
    print("\n" + "=" * 64)
    print("MISTRAL  (không có endpoint quota; đọc rate-limit từ header)")
    print("=" * 64)
    if r.get("error") and r.get("http") != 200:
        print("  LỖI:", r["error"])
        return
    print(f"  Khóa hợp lệ, {r.get('models')} model")
    rl = r.get("rate_limit") or {}
    if rl:
        print(f"  Model đo    : {r.get('test_model')}")
        print(f"  Token/phút : {rl.get('x-ratelimit-remaining-tokens-minute')} "
              f"/ {rl.get('x-ratelimit-limit-tokens-minute')}")
        print(f"  Request/phút: {rl.get('x-ratelimit-remaining-req-minute')} "
              f"/ {rl.get('x-ratelimit-limit-req-minute')}")
        print("  (rate-limit khác nhau theo từng model — dùng --mistral-model để đo model khác)")
    else:
        print("  Không đọc được header rate-limit (request thử: "
              f"{r.get('test_http')})")
    if r.get("test_http") == 429:
        print("  ← ĐANG CHẠM HẠN MỨC TỐC ĐỘ")


def print_google(r: dict) -> None:
    print("\n" + "=" * 64)
    print("GOOGLE GEMINI  (không có endpoint quota; dò bằng 1 request thật)")
    print("=" * 64)
    if r.get("http") != 200:
        print("  LỖI:", r.get("error"))
        return
    print(f"  Khóa hợp lệ, {r.get('models')} model")
    st = r.get("test_http")
    if r.get("test_model"):
        print(f"  Model thử   : {r.get('test_model')}")
    if st == 200:
        print("  Request thử: 200 → còn hạn mức")
    elif st == 429:
        print("  Request thử: 429 → HẾT hạn mức (free tier), chờ reset")
    else:
        print(f"  Request thử: {st} → {r.get('error', '')}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra hạn mức các API đã kết nối")
    ap.add_argument("--json", action="store_true", help="xuất JSON thay vì bảng")
    ap.add_argument("--chi-go", action="store_true", help="chỉ kiểm tra OpenCode Go")
    ap.add_argument("--mistral-model", default="mistral-small-2603",
                    help="model Mistral dùng để đo rate-limit (mặc định mistral-small-2603)")
    args = ap.parse_args()

    creds = read_credentials()
    if not creds:
        print("Không tìm thấy credential nào. Chạy /connect trong OpenCode trước.")
        return 1

    results = []
    if "opencode-go" in creds:
        results.append(check_go(creds["opencode-go"]))
    if not args.chi_go:
        if "mistral" in creds:
            results.append(check_mistral(creds["mistral"], args.mistral_model))
        if "google" in creds:
            results.append(check_google(creds["google"]))

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    for r in results:
        if r["provider"].startswith("OpenCode"):
            print_go(r)
        elif r["provider"].startswith("Mistral"):
            print_mistral(r)
        else:
            print_google(r)

    missing = [n for n in ("opencode-go", "mistral", "google") if n not in creds]
    if missing:
        print("\nChưa kết nối: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
