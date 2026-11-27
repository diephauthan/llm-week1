# from dotenv import load_dotenv
# from google import genai
# from google.genai import types, errors
# import time

# load_dotenv()               #read GEMINI_API_KEY from file .env
# client = genai.Client()     #tự lấy key từ biến mt
# MODEL = "gemini-3.8-flash"  #nếu báo lỗi model, thì chạy list_model() rồi đổi tên

# def list_models():
#     for m in client.models.list():
#         print(m.name)


# FALLBACK_MODELS = [MODEL, "gemini-3.7-flash", "gemini-3.5-flash-lite"]

# def generate(**kwargs):
#     """Gọi generate_content, tự thử lại khi server bận, rồi chuyển sang model dự phòng."""
#     for model in FALLBACK_MODELS:
#         for i in range(3):
#             try:
#                 return client.models.generate_content(model=model, **kwargs)
#             except errors.ServerError as e:
#                 wait = 2 ** i
#                 print(f"[{model}] server bận ({e.code}), thử lại sau {wait}s")
#                 time.sleep(wait)
#         print(f"[{model}] vẫn bận, chuyển sang model khác")
#     raise RuntimeError("tất cả model đang bận")

# def ask(question: str, temperature: float = 0.2, system: str | None = None, max_output_tokens: int = 1000):
#     """Hỏi model một câu, trả về (text, tokens)."""
#     #1 create config
#     config = types.GenerateContentConfig(
#         temperature= temperature,
#         system_instruction=system,
#         max_output_tokens=max_output_tokens,
#     )

#     #2. gọi model
#     resp= generate(contents=question, config=config)

#     # 3. đêm token
#     u = resp.usage_metadata
#     tokens= {
#         "input": u.prompt_token_count,
#         "output": u.candidates_token_count or 0,
#         "thinking": u.thoughts_token_count or 0,
#         "total": u.total_token_count,
#     }

#     if resp.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
#         print("⚠ Câu trả lời bị cắt vì chạm max_output_tokens")
    
#     return resp.text or "", tokens

from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()      # tự đọc ANTHROPIC_API_KEY
MODEL = "claude-haiku-5-5"