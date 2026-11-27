from typing import Literal
from pydantic import BaseModel, ValidationError, model_validator


class MaintenanceReport(BaseModel):
    machine_id: str | None
    tool_type: str | None
    predicted_wear_um: float | None
    wear_limit_um: float | None
    risk_level: Literal["low", "medium", "high", "unknown"]
    requested_actions: list[str]     # người dùng hỏi / yêu cầu gì
    suggested_actions: list[str]     # trợ lý tự đề xuất gì
    explanation: str                 # một câu giải thích cho thợ

    @model_validator(mode="after")
    def check_risk(self):
        if self.predicted_wear_um is not None and self.wear_limit_um is not None:
            if self.predicted_wear_um >= self.wear_limit_um and self.risk_level != "high":
                raise ValueError("Mòn đã chạm giới hạn nhưng risk_level không phải 'high'")
        return self


if __name__ == "__main__":
    good = {
        "machine_id": "CNC-03", "tool_type": "end mill",
        "predicted_wear_um": 258.8, "wear_limit_um": 300, "risk_level": "medium",
        "requested_actions": ["Kiểm tra dao còn dùng được không"],
        "suggested_actions": ["Lên kế hoạch thay dao sớm"],
        "explanation": "Mòn 258.8 µm, còn dưới giới hạn 300 µm.",
    }
    print(MaintenanceReport(**good))

    bad = {**good, "predicted_wear_um": 320}     # copy good, chỉ đổi độ mòn
    try:
        MaintenanceReport(**bad)
    except ValidationError as e:
        print("Lỗi:", e)