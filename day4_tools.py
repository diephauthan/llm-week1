import json
import sys

from anthropic import beta_tool
from common import client, MODEL


# ============================================================
# 1. HÀM PYTHON THẬT (tool)
#    Claude chỉ nhận lại CHUỖI → trả về json.dumps(dict)
# ============================================================
def predict_tool_wear(cutting_force_n: float, cutting_time_min: float) -> str:
    """Predict flank wear (micrometers) of an end mill.

    Args:
        cutting_force_n: mean resultant cutting force in newtons.
        cutting_time_min: accumulated cutting time in minutes.
    """
    # Tạm dùng công thức kiểu Archard. Ngày 6 thay bằng mô hình thật.
    k = 0.0009
    wear = k * cutting_force_n * cutting_time_min
    return json.dumps({"wear_um": round(wear, 1)})


def get_wear_limit(tool_type: str) -> str:
    """Return the maximum allowed flank wear (micrometers) for a tool type.

    Args:
        tool_type: tool type, e.g. 'end mill' or 'drill'.
    """
    limits = {"end mill": 300, "drill": 250}
    return json.dumps({"limit_um": limits.get(tool_type.lower(), 300)})


# Bảng tra: tên tool (model gửi về) → hàm Python cần chạy
TOOLS = {
    "predict_tool_wear": predict_tool_wear,
    "get_wear_limit": get_wear_limit,
}

# ============================================================
# 2. MÔ TẢ TOOL CHO MODEL (viết tay, dùng cho cách 2)
#    Đây chính là thứ model "đọc" để quyết định gọi tool nào.
#    description viết kỹ = model gọi đúng hơn.
# ============================================================
TOOL_SPECS = [
    {
        "name": "predict_tool_wear",
        "description": (
            "Predict flank wear (micrometers) of an end mill from the mean "
            "cutting force and the accumulated cutting time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cutting_force_n": {
                    "type": "number",
                    "description": "mean resultant cutting force in newtons",
                },
                "cutting_time_min": {
                    "type": "number",
                    "description": "accumulated cutting time in minutes",
                },
            },
            "required": ["cutting_force_n", "cutting_time_min"],
        },
    },
    {
        "name": "get_wear_limit",
        "description": "Return the maximum allowed flank wear (micrometers) for a tool type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tool_type": {
                    "type": "string",
                    "description": "tool type, e.g. 'end mill' or 'drill'",
                },
            },
            "required": ["tool_type"],
        },
    },
]

QUESTION = (
    "End mill on CNC-03: average force 820 N, cut for 350 minutes. "
    "Should we replace it now?"
)




def get_text(resp) -> str:
    """Ghép các khối text (bỏ qua khối thinking / tool_use)."""
    return "".join(b.text for b in resp.content if b.type == "text")


# ============================================================
# CÁCH 1 – TỰ ĐỘNG: tool runner của SDK tự chạy hàm và gửi kết quả về
#   beta_tool(f) đọc type hint + docstring → tự dựng TOOL_SPECS
# ============================================================
def run_auto(question: str) -> str:
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=2000,
        max_iterations=5,                       # giới hạn số vòng
        tools=[beta_tool(f) for f in TOOLS.values()],
        messages=[{"role": "user", "content": question}],
    )
    # Thay vì until_done(), duyệt từng message để xem bên trong làm gì
    tokens_in = tokens_out = 0
    final = None
    for step, message in enumerate(runner):     # mỗi vòng = 1 lần gọi API
        tokens_in += message.usage.input_tokens
        tokens_out += message.usage.output_tokens
        for block in message.content:
            if block.type == "tool_use":
                print(f"Step {step}: {block.name}({block.input})")
        final = message
    print(f"  [stop_reason={final.stop_reason}, "
          f"tokens in/out = {tokens_in}/{tokens_out}]")
    return get_text(final)


# ============================================================
# CÁCH 2 – TỰ VIẾT VÒNG LẶP AGENT
# ============================================================
def run_agent(question: str, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": question}]
    tokens_in = tokens_out = 0

    for step in range(max_steps):               # giới hạn bước, tránh lặp vô hạn
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            tools=TOOL_SPECS,
            messages=messages,
        )
        tokens_in += resp.usage.input_tokens
        tokens_out += resp.usage.output_tokens

        # Không xin gọi tool nữa → đã có câu trả lời cuối
        if resp.stop_reason != "tool_use":
            print(f"  [stop_reason={resp.stop_reason}, "
                  f"tokens in/out = {tokens_in}/{tokens_out}]")
            return get_text(resp)

        # Giữ NGUYÊN resp.content (gồm cả khối thinking và tool_use)
        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                print(f"  (model nói) {block.text.strip()}")
            if block.type != "tool_use":
                continue
            print(f"Step {step}: {block.name}({block.input})")
            try:
                output = TOOLS[block.name](**block.input)
                is_error = False
            except Exception as e:              # tool lỗi → báo cho model tự xử lý
                output = f"{type(e).__name__}: {e}"
                is_error = True
            print(f"   -> {output}")
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,        # phải khớp id của yêu cầu
                "content": output,
                "is_error": is_error,
            })

        # Kết quả tool gửi về dưới role "user"
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"Agent chưa xong sau {max_steps} bước")


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else QUESTION

    print("=== Cách 1: tool runner (tự động) ===")
    print(run_auto(q))

    print("\n=== Cách 2: vòng lặp tự viết ===")
    print("FINAL:", run_agent(q))