from agent import ask

RUNS = 3                       # mỗi câu chạy 3 lần
PRICE_IN, PRICE_OUT = 0.10, 0.50   # USD / 1M token (claude-haiku-5-5)

H = "get_machine_history"
P = "predict_tool_wear"
L = "get_wear_limit"

# ok_tools: các bộ tool chấp nhận được (so theo tập hợp, không tính thứ tự)
# wear: độ mòn đúng trong báo cáo; None = phải để trống; không có khóa = không kiểm tra
CASES = [
    {"q": "Dao trên CNC-03 còn dùng được không?",           "ok_tools": [{H, P, L}], "wear": 258.8},
    {"q": "Is the tool on CNC-05 still OK?",                 "ok_tools": [{H, P, L}], "wear": 29.2},
    {"q": "Dao trên CNC-99 còn dùng được không?",            "ok_tools": [{H}],       "wear": None},
    {"q": "Mòn dao là gì?",                                  "ok_tools": [set()],     "wear": None},
    {"q": "Giới hạn mòn của mũi khoan là bao nhiêu?",        "ok_tools": [{L}],       "wear": None},
    {"q": "Why does tool wear increase with cutting force?", "ok_tools": [set()],     "wear": None},
    {"q": "Dao phay ngón chịu lực 820 N, đã cắt 350 phút. Có cần thay chưa?",
                                                             "ok_tools": [{P, L}],    "wear": 258.3},
    {"q": "Máy CNC-03 đã cắt tổng cộng bao nhiêu phút?",     "ok_tools": [{H}]},
    {"q": "Dao chịu lực -50 N, cắt 100 phút thì mòn bao nhiêu?",
                                                             "ok_tools": [{P}, set()], "wear": None},
    {"q": "So sánh tình trạng dao của CNC-03 và CNC-05.",    "ok_tools": [{H, P, L}]},
]


def check(case, r):
    """Trả về danh sách lỗi của một lần chạy (rỗng = đạt)."""
    errors = []
    if set(r["tools"]) not in case["ok_tools"]:
        errors.append(f"tool: gọi {sorted(set(r['tools']))}")
    if r["report"] is None:
        errors.append("không có báo cáo")
    elif "wear" in case:
        got = r["report"].predicted_wear_um
        want = case["wear"]
        if want is None and got is not None:
            errors.append(f"mòn: lẽ ra để trống, nhận {got}")
        elif want is not None and (got is None or abs(got - want) > 0.5):
            errors.append(f"mòn: lẽ ra {want}, nhận {got}")
    return errors


def main():
    total_pass, total_in, total_out = 0, 0, 0
    for i, case in enumerate(CASES, 1):
        n_pass, notes = 0, []
        for run in range(RUNS):
            try:
                r = ask(case["q"], verbose=False)
            except Exception as e:
                notes.append(f"lỗi API: {e}")
                continue
            total_in += r["tokens"]["in"]
            total_out += r["tokens"]["out"]
            errors = check(case, r)
            if errors:
                notes.append("; ".join(errors))
            else:
                n_pass += 1
        total_pass += n_pass
        print(f"{i:2d}. {n_pass}/{RUNS}  {case['q']}")
        for note in notes:
            print(f"      - {note}")

    n_total = len(CASES) * RUNS
    cost = total_in / 1e6 * PRICE_IN + total_out / 1e6 * PRICE_OUT
    print(f"\nTổng: {total_pass}/{n_total} = {total_pass / n_total:.0%}")
    print(f"Token: {total_in} vào, {total_out} ra, khoảng ${cost:.4f}")


if __name__ == "__main__":
    main()
