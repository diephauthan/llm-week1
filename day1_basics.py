from google.genai import types
from common import client, MODEL


# 1. gọi cơ bản
resp = client.models.generate_content(
    model = MODEL,
    contents="explain tool wear in CNC milling in 3 sentences.",
)
print(resp.text)

# 2. thêm system instruction và tham số
config = types.GenerateContentConfig(
    system_instruction="you are a maintenance engineer. Answer briefly, in Vietnamese.",
    temperature=0.2,
)
print(resp.text)
print(resp.usage_metadata)

#3. streaming: in ra từng đoạn ngay khi model sinh xong
for chuck in  client.models.generate_content_stream(
    model=MODEL, contents="write a 150-word story about a tired cnc machine."
):
    print(chuck.text, end="", flush=True)

#4. hội thoại nhiều lượt chat tự giữ lịch sử
chat=client.chats.create(model=MODEL)
print(chat.send_message("my name is diep. i study tool wear").text)
print(chat.send_message("what is my research topic?").text)

