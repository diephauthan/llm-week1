import numpy as np
from fastembed import TextEmbedding
from day8_embedding import MODEL_NAME

docs = [
    "Flank wear (VB) is measured on the flank face of the cutting edge; a common tool-life criterion is VB = 0.3 mm.",
    "Mòn mặt trước (crater wear) tạo thành hố lõm trên mặt trước của dao, thường do nhiệt độ cao khi cắt thép.",
    "Increasing cutting speed raises the temperature at the tool tip and shortens tool life (Taylor's equation).",
    "Khi khoan thép không gỉ, nên dùng tốc độ cắt thấp và tưới nguội đầy đủ để tránh gãy mũi khoan.",
    "Coolant concentration should be checked regularly with a refractometer.",
    "Độ nhám bề mặt tăng đột ngột là dấu hiệu dao đã mòn và cần kiểm tra.",
    "Spindle bearings should be lubricated according to the machine maintenance schedule.",
    "Dao phay ngón phủ TiAlN phù hợp gia công thép đã tôi ở tốc độ cao.",
]

model = TextEmbedding(model_name=MODEL_NAME)

def embed(texts):
    """Biến list câu thành ma trận vector đã chuẩn hóa (độ dài 1)."""
    E = np.array(list(model.embed(texts)))
    return E / np.linalg.norm(E, axis=1, keepdims=True)

def search(query, D, docs, k=3):
    """Trả về k cặp (điểm cosine, đoạn văn) giống câu hỏi nhất."""
    q=embed([query])[0]
    scores = D @ q
    top = np.argsort(-scores)[:k]
    return [(float(scores[i]), docs[i]) for i in top]

if __name__ == "__main__":
    D = embed(docs)

    # questions = [
    #     "Khi nào thì phải thay dao? Tiêu chuẩn mòn mặt sau là bao nhiêu?",
    #     "Why does tool life drop at high cutting speed?",
    #     "Làm sao tránh gãy mũi khoan inox?",
    #     "Giá vàng hôm nay bao nhiêu?",
    # ]
    questions = [
        "Khi nào thì phải thay dao? Tiêu chuẩn mòn mặt sau là bao nhiêu?",   # gốc
        "Tiêu chuẩn mòn mặt sau là bao nhiêu?",                             # bỏ ý 1, vẫn tiếng Việt
        "Tiêu chuẩn mòn mặt sau (flank wear) là bao nhiêu?",                # thêm thuật ngữ tiếng Anh
        "What is the flank wear criterion for replacing a tool?",           # hoàn toàn tiếng Anh
    ]
    for question in questions:
        print(f"\nHỏi: {question}")
        for score, text in search(question, D, docs):
            print(f"  {score:.2f}  {text[:70]}")


model = TextEmbedding(model_name=MODEL_NAME)
