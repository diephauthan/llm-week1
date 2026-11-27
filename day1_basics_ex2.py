from google.genai import types
from common import MODEL, client, generate

for limit in [20, 200, 1000]:
    # resp = client.models.generate_content(
    #     model=MODEL,
    #     contents="explain tool wear in cnc milling in 3 sentences.",
    #     config = types.GenerateContentConfig(max_output_tokens=limit),
    # )
    resp= generate(contents="Explain tool wear in CNC milling in 3 sentences.",
                   config=types.GenerateContentConfig(max_output_tokens=limit),)
    cand=resp.candidates[0]
    u = resp.usage_metadata
    print(f"\n--- max_output_tokens = {limit}")
    print("finish_reason:", cand.finish_reason)
    print("token suy nghĩ:", u.thoughts_token_count, "| token trả lời", u.candidates_token_count)
    print("text:", resp.text)