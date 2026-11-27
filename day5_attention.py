# day5_attention.py – tự viết self-attention bằng numpy
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)


# ---------------------------------------------------------------
# 1. Softmax theo từng hàng: đổi điểm thành phần trăm (mỗi hàng cộng = 1)
# ---------------------------------------------------------------
def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


print("=== 1. Softmax bão hòa khi điểm lớn ===")
print(softmax(np.array([1.0, 2.0, 3.0])).round(3))
print(softmax(np.array([10.0, 20.0, 30.0])).round(3))


# ---------------------------------------------------------------
# 2. Vì sao chia √d_k: điểm Q·K to dần theo √d_k
# ---------------------------------------------------------------
print("\n=== 2. Điểm Q·K tăng theo √d_k ===")
for d_k in [4, 64, 512]:
    Q = rng.standard_normal((1000, d_k))
    K = rng.standard_normal((1000, d_k))
    scores = (Q * K).sum(axis=1)
    print(d_k, "| std chưa chia:", scores.std().round(1),
               "| std sau chia √d_k:", (scores / np.sqrt(d_k)).std().round(2))


# ---------------------------------------------------------------
# 3. Hàm attention: softmax(QKᵀ / √d_k) · V, có tùy chọn che tương lai
# ---------------------------------------------------------------
def attention(Q, K, V, causal=False):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)

    if causal:                                   # GPT: không được nhìn token phía sau
        n = scores.shape[0]
        mask = np.triu(np.ones((n, n)), k=1).astype(bool)
        scores = np.where(mask, -np.inf, scores)  # e^(-∞) = 0 → 0%

    weights = softmax(scores)
    return weights @ V, weights


def show(weights, tokens):
    """In bảng trọng số có tên hàng/cột cho dễ đọc."""
    print(pd.DataFrame(weights, index=tokens, columns=tokens).round(2))


# ---------------------------------------------------------------
# 4. Một câu 3 token: Q, K, V sinh ra từ embedding X qua 3 ma trận W
# ---------------------------------------------------------------
tokens = ["tool", "wear", "fast"]
d_model, d_k = 8, 4

X = rng.standard_normal((3, d_model))            # embedding của 3 token (3 × 8)

# Chia √d_model để Q, K, V không quá to (model thật cũng khởi tạo như vậy)
W_Q = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)
W_K = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)
W_V = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)

Q, K, V = X @ W_Q, X @ W_K, X @ W_V              # mỗi cái 3 × 4

out, w = attention(Q, K, V)
print("\n=== 3. Attention KHÔNG che (kiểu BERT) ===")
show(w, tokens)

out_c, w_c = attention(Q, K, V, causal=True)
print("\n=== 4. Attention CÓ che tương lai (kiểu GPT) ===")
show(w_c, tokens)
print("out shape:", out_c.shape)


# ---------------------------------------------------------------
# 5. Multi-head: nhiều bộ W_Q, W_K, W_V chạy song song, rồi nối lại
# ---------------------------------------------------------------
n_heads = 2
heads = []

print("\n=== 5. Multi-head (2 head) ===")
for h in range(n_heads):
    W_Q = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)
    W_K = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)
    W_V = rng.standard_normal((d_model, d_k)) / np.sqrt(d_model)

    out_h, w_h = attention(X @ W_Q, X @ W_K, X @ W_V, causal=True)
    print(f"-- head {h} --")
    show(w_h, tokens)
    heads.append(out_h)

concat = np.concatenate(heads, axis=-1)          # 3 × (2·4) = 3 × 8
W_O = rng.standard_normal((n_heads * d_k, d_model)) / np.sqrt(n_heads * d_k)
final = concat @ W_O                             # 3 × 8, cùng cỡ với X

print("concat shape:", concat.shape, "| final shape:", final.shape, "| X shape:", X.shape)