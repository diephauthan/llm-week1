# day2_prompt_eval.py – so sánh các prompt trên cùng bộ dữ liệu có nhãn
import re
from common import client, MODEL

# ---------------------------------------------------------------
# Bước 2: Dataset – mỗi phần tử là (dòng log, nhãn đúng)
# TODO chiều nay: viết thêm cho đủ 20 mẫu, có vài mẫu "khó"
# ---------------------------------------------------------------
dataset = [
    # --- NORMAL dễ ---
    ("Spindle vibration 2.1 mm/s, temperature 45C, stable for 3 hours", "NORMAL"),
    ("Coolant flow normal, surface roughness Ra 0.8 um as usual", "NORMAL"),
    ("New end mill installed, first 10 parts within tolerance", "NORMAL"),
    ("Cutting force steady at 780 N for the whole shift, no unusual noise", "NORMAL"),
    ("Spindle load 45%, chips silver and evenly curled", "NORMAL"),
    ("Dimensional check OK on 50 parts, no burr observed", "NORMAL"),
    ("Coolant concentration 6%, pressure 20 bar, machine running smoothly", "NORMAL"),
    # --- FAULT dễ ---
    ("Cutting force rose 35% in 10 minutes, loud chatter noise", "FAULT"),
    ("Visible chipping on cutting edge, burr on part surface", "FAULT"),
    ("Tool broke during cut, part scrapped", "FAULT"),
    ("Spindle temperature 85C and alarm triggered, machine stopped", "FAULT"),
    ("Chips turned blue and smoke observed at the cutting zone", "FAULT"),
    ("Coolant pump failed, no flow to the tool for 5 minutes", "FAULT"),
    ("Flank wear measured 380 um, above the 300 um limit", "FAULT"),
    # --- Mẫu khó ---
    ("Vibration 3.4 mm/s, slightly higher than yesterday but within spec", "NORMAL"),
    ("Small burr on the first part after tool change, next parts are clean", "NORMAL"),
    ("Cutting force up 8% over 2 hours, no noise, surface still fine", "NORMAL"),
    ("Flank wear measured 240 um on end mill, limit is 300 um", "NORMAL"),
    ("Surface roughness Ra rose from 0.8 to 1.6 um over the shift", "FAULT"),
    ("Spindle temperature 62C after 4 hours, rising about 1C every 10 minutes", "FAULT"),
]

# ---------------------------------------------------------------
# Bước 3: Khuôn prompt – {log} là chỗ trống, điền bằng .format()
# TODO: thêm PROMPT_C (few-shot) và PROMPT_D (chain-of-thought)
# ---------------------------------------------------------------
PROMPT_A = "Classify this machine log as NORMAL or FAULT:\n{log}"

PROMPT_B = """You are a senior CNC maintenance engineer.
Classify the machine log below.
FAULT means a likely problem with the tool or machine (sudden force increase, chatter, chipping, overheating).
NORMAL means stable operation.

<log>{log}</log>

Answer with exactly one word: NORMAL or FAULT."""


# ---------------------------------------------------------------
# Hàm đọc nhãn "dễ tính": lấy chữ NORMAL/FAULT xuất hiện CUỐI CÙNG
# (dùng được cho cả câu trả lời dài, ví dụ chain-of-thought)
# ---------------------------------------------------------------
def parse_label(text):
    if not text:
        return "EMPTY"
    found = re.findall(r"\b(NORMAL|FAULT)\b", text.upper())
    return found[-1] if found else "UNPARSED"


# ---------------------------------------------------------------
# Bước 4: Chạy 1 prompt trên toàn bộ dataset và chấm điểm
# ---------------------------------------------------------------
def run(prompt_template):
    strict_correct = 0     # khớp chính xác từng chữ
    lenient_correct = 0    # đúng nhãn sau khi parse_label

    for log, label in dataset:
        prompt = prompt_template.format(log=log)          # điền log vào khuôn

        resp = client.messages.create(                     # gọi model
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        # resp.content là list các "khối": có thể có khối thinking trước khối text
        text = "".join(block.text for block in resp.content if block.type == "text")

        strict_pred = text.strip().upper()
        lenient_pred = parse_label(text)

        strict_correct += (strict_pred == label)           # True = 1, False = 0
        lenient_correct += (lenient_pred == label)

        if lenient_pred != label:
            print(f"  SAI NHÃN   : {log[:50]} -> {lenient_pred}")
        elif strict_pred != label:
            print(f"  SAI ĐỊNH DẠNG: {log[:50]} -> {text!r}")

    n = len(dataset)
    return strict_correct / n, lenient_correct / n


# ---------------------------------------------------------------
# Bước 5: Chạy và in kết quả
# ---------------------------------------------------------------
for name, template in [("A", PROMPT_A), ("B", PROMPT_B)]:
    print(f"\n=== Prompt {name} ===")
    strict_acc, lenient_acc = run(template)
    print(f"strict accuracy : {strict_acc:.0%}")
    print(f"lenient accuracy: {lenient_acc:.0%}")