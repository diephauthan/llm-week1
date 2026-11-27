import json
import sqlite3
from db import DB_PATH

def get_machine_history(machine_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT tool_type,
               SUM(cutting_time_min),
               AVG(mean_force_n),
               COUNT(*)
        FROM runs
        WHERE machine_id = ?
        GROUP BY tool_type
    """, (machine_id,)).fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"Không tìm thấy máy {machine_id}")

    result = [{"tool_type": t, "total_cutting_time_min": total,
               "mean_force_n": round(force, 1), "n_runs": n}
              for t, total, force, n in rows]
    return json.dumps(result, ensure_ascii=False)

def predict_tool_wear(cutting_force_n: float, cutting_time_min: float) -> str:
    """Predict flank wear (micrometers) of an end mill.

    Args:
        cutting_force_n: mean resultant cutting force in newtons.
        cutting_time_min: accumulated cutting time in minutes.
    """
    # Tạm dùng công thức kiểu Archard. Ngày 6 thay bằng mô hình thật.
    if cutting_force_n <= 0:
        raise ValueError(f"Lực cắt phải lớn hơn 0 N, nhận được {cutting_force_n} N")
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

TOOL_SPECS = [
    {
        "name": "get_machine_history",
        "description": "Look up a CNC machine's cutting history. Returns, per tool type, "
                       "total cutting time (min), mean cutting force (N) and number of runs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "machine_id": {"type": "string", "description": "Machine ID, e.g. 'CNC-03'."}
            },
            "required": ["machine_id"],
        },
    },
    {
        "name": "predict_tool_wear",
        "description": "Predict flank wear (micrometers) from mean cutting force and accumulated cutting time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cutting_force_n": {"type": "number", "description": "Mean cutting force in newtons."},
                "cutting_time_min": {"type": "number", "description": "Accumulated cutting time in minutes."},
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
                "tool_type": {"type": "string", "description": "Tool type, e.g. 'end mill' or 'drill'."}
            },
            "required": ["tool_type"],
        },
    },
]

TOOLS = {
    "get_machine_history": get_machine_history,
    "predict_tool_wear": predict_tool_wear,
    "get_wear_limit": get_wear_limit,
}

if __name__ == "__main__":
    print(get_machine_history("CNC-03"))
    print(predict_tool_wear(820, 350))
    print(get_wear_limit("end mill"))
    print(TOOLS["predict_tool_wear"](**{"cutting_force_n": 820, "cutting_time_min": 350}))
    try:
        predict_tool_wear(-50,305)
    except ValueError as e:
        print("Lỗi:", e)

    