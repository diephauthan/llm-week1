import numpy as np
from fastembed import TextEmbedding

MODEL_NAME ="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

sentences = [
    "Mòn mặt sau của dao phay đã vượt 0,3 mm",      # 0
    "Flank wear of the end mill exceeded 0.3 mm",    # 1  (cùng nghĩa câu 0, tiếng Anh)
    "Dao phay ngón bị mòn nhiều, cần thay dao",      # 2
    "Tốc độ trục chính là 8000 vòng/phút",           # 3
    "Spindle speed is set to 8000 rpm",              # 4  (cùng nghĩa câu 3)
    "Mũi khoan bị gãy khi khoan thép không gỉ",      # 5
    "The coolant tank needs to be refilled",         # 6
    "Hôm nay trời mưa to ở Hà Nội",                  # 7  (không liên quan CNC)
]

if __name__ == "__main__":
    model = TextEmbedding(model_name=MODEL_NAME)
    E = np.array(list(model.embed(sentences)))
    print("kích thước E:", E.shape)
    print("độ dài từng vector:", np.linalg.norm(E, axis=1).round(3))

    E_norm = E / np.linalg.norm(E, axis=1, keepdims=True)
    S= E_norm @ E_norm.T

    np.set_printoptions(precision=2, suppress=True)
    print("\nBảng cosine (hàng i, cột j = độ giống câu i và câu j):")
    print(S)

    order = np.argsort(-S[0])
    print(f"\n gần nhất với: {sentences[0]}")
    for i in order[1:4]:
        print(f"  {S[0, i]:.2f}  [{i}] {sentences[i]}")
