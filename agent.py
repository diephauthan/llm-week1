from common import client, MODEL
from tools import TOOL_SPECS, TOOLS
import json
from report import MaintenanceReport

SYSTEM = (
    "You are a CNC maintenance assistant for machine operators. "
    "Use the tools to look up machine history, predict tool wear and get the wear limit. "
    "Never compute numbers yourself; only use numbers returned by tools. "
    "Answer in the user's language, short and clear."
)

REPORT_PROMPT = """Fill in a maintenance report from the conversation below.
Rules:
- Use only numbers that appear in the tool results. Do not compute new numbers.
- If a value is unknown (no tool result for it), use null.
- risk_level: "high" if predicted wear >= wear limit, "medium" if >= 80% of the limit,
  "low" if below 80%, "unknown" if there is no wear prediction.
- requested_actions: only what the user asked for.
- suggested_actions: your own suggestions (for example: plan a tool change).
- explanation: one short sentence for the machine operator, in the user's language.

<question>{question}</question>
<tool_results>
{tool_log}
</tool_results>
<answer>{answer}</answer>"""

def run_agent(question, max_steps = 5, verbose=True):
    messages= [{"role": "user", "content": question}]
    tool_log = []
    tokens = {"in": 0, "out": 0}

    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL,
            messages= messages,
            max_tokens= 2000,
            system = SYSTEM,
            tools= TOOL_SPECS
        )
        tokens["in"] += resp.usage.input_tokens
        tokens["out"] += resp.usage.output_tokens

        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text")
            return answer, tool_log, tokens
        
        messages.append({"role": "assistant", "content": resp.content})
        results=[]

        for block in resp.content:
            if block.type != "tool_use":
                continue
            try:
                output = TOOLS[block.name](**block.input)
                is_error = False
            except Exception as e:
                output = f"Lỗi: {e}"
                is_error = True
            if verbose:
                print(f"  [tool] {block.name}({block.input}) -> {output}")
            tool_log.append({"name": block.name, "input": block.input,
                             "output": output, "is_error": is_error})
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})

    return "Hết số bước cho phép.", tool_log, tokens

def make_report(question, answer, tool_log, tokens, max_retries=2):
    """Lời gọi thứ 2: điền MaintenanceReport. Sai luật thì gửi lỗi cho model sửa."""
    log_text = "\n".join(
        f"- {t['name']}({json.dumps(t['input'], ensure_ascii=False)}) -> {t['output']}"
        for t in tool_log
    ) or "(no tools called)"
    prompt = REPORT_PROMPT.format(question=question, tool_log=log_text, answer=answer)

    error_note =""
    for attempt in range(max_retries + 1):
        try:
            resp = client.messages.parse(
                model=MODEL, max_tokens=2000,
                messages=[{"role": "user", "content": prompt + error_note}],
                output_format=MaintenanceReport,
            )
            tokens["in"] += resp.usage.input_tokens
            tokens["out"] += resp.usage.output_tokens
            if resp.parsed_output is None:
                error_note = "\n\nYour previous reply was not a valid report. Try again."
                continue
            # chạy lại luật check_risk cho chắc chắn
            return MaintenanceReport.model_validate(resp.parsed_output.model_dump())
        except ValueError as e:          # ValidationError của Pydantic cũng là ValueError
            error_note = f"\n\nYour previous report was rejected:\n{e}\nFix it."
    return None

def ask(question, verbose=True):
    """Hỏi một câu: chạy agent rồi tạo báo cáo."""
    answer, tool_log, tokens = run_agent(question, verbose=verbose)
    report = make_report(question, answer, tool_log, tokens)
    return {"answer": answer, "report": report,
            "tools": [t["name"] for t in tool_log], "tokens": tokens}


if __name__ == "__main__":
    r = ask("Dao trên CNC-03 còn dùng được không?")
    print("Trợ lý:", r["answer"])
    print("Báo cáo:")
    print(r["report"].model_dump_json(indent=2) if r["report"] else None)
    print("Token:", r["tokens"])