# day3_structured.py – ép Claude trả về JSON đúng schema, kiểm tra bằng Pydantic, tự sửa khi sai
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from common import client, MODEL


# ---------------------------------------------------------------
# 1. "Mẫu phiếu" mà Claude phải điền
# ---------------------------------------------------------------
class Severity(str, Enum):          # chỉ được chọn 1 trong 3 giá trị
    low = "low"
    medium = "medium"
    high = "high"


class MaintenanceReport(BaseModel):
    machine_id: str
    tool_type: str = Field(description="e.g. end mill, drill")
    estimated_wear_um: float = Field(ge=0, description="flank wear in micrometers")
    severity: Severity
    actions: list[str] = Field(description="recommended actions, max 3")


# ---------------------------------------------------------------
# 2. Ghi chú viết tay của thợ (dữ liệu đầu vào)
# ---------------------------------------------------------------
note = """Ca đêm 19/11, máy CNC-03. Dao phay ngón Ø10 chạy 6 tiếng liên tục.
Đo miệng dao thấy mòn khoảng 180 micromet, bề mặt chi tiết bắt đầu có ba via.
Thợ đề nghị kiểm tra nước làm mát."""


# ---------------------------------------------------------------
# 3. Trích xuất, có vòng retry: sai thì gửi lỗi lại cho Claude tự sửa
# ---------------------------------------------------------------
def extract(text: str, retries: int = 2) -> MaintenanceReport:
    prompt = f"Extract a maintenance report from this note:\n<note>{text}</note>"

    for attempt in range(retries + 1):
        try:
            resp = client.messages.parse(
                model=MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
                output_format=MaintenanceReport,   # Pydantic class = schema
            )
            # SDK đã tự kiểm tra bằng Pydantic; tới được đây là hợp lệ
            return resp.parsed_output

        except ValidationError as e:
            print(f"Lần {attempt + 1} sai schema:\n{e}\n")
            prompt += f"\n\nYour previous output was invalid: {e}. Fix it."

    raise RuntimeError("Không trích xuất được sau nhiều lần thử")


# ---------------------------------------------------------------
# 4. Chạy thử
# ---------------------------------------------------------------
report = extract(note)
print(report.model_dump_json(indent=2))   # object → JSON đẹp để in
print("Độ mòn + 20 =", report.estimated_wear_um + 20)   # dùng như dữ liệu thật