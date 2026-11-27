from common import client, MODEL
from day4_tools import TOOLS, TOOL_SPECS

def run_agent(question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(max_steps):
        resp = client.messages.create(
            model = MODEL,
            messages=messages,
            max_tokens=2000,
            tools=TOOL_SPECS
        )

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            try:
                output= TOOLS[block.name](**block.input)
                is_error = False
            except Exception as e:
                output = f"lỗi: {e}"
                is_error = True
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output, "is_error": is_error})
            
        messages.append({"role": "user", "content": results})

    return "hết số bước cho phép"

if __name__ == "__main__":
    print(run_agent("dao chịu lực 820N, đã cắt 350 phút. có cần thay chưa?"))