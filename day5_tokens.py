from transformers import AutoTokenizer
from common import MODEL, client

name = "Qwen/Qwen2.5-0.5B-Instruct"
tok= AutoTokenizer.from_pretrained(name)

# for text in ["tool wear", "mòn dao", "physics-informed neural network"]:
#     ids= tok(text)["input_ids"]
#     print(text, "->", len(ids), "token:", [tok.decode([i]) for i in ids])

pairs={
    "EN": "The flank wear of the end mill exceeded 300 microns, so the tool must be replaced",
    "VN": "Mòn mặt sau của dao phay ngón đã vượt quá 300 micromet, nên phải thay dao",
}

# for lang, text in pairs.items():
#     n_tok = len(tok(text)["input_ids"])
#     print(lang, "->", n_tok, "tokens")

for lang, text in pairs.items():
    r = client.messages.count_tokens(
        model = MODEL,
        messages=[{"role": "user", "content": text}],
    )
    print(lang, "->", r.input_tokens, "tokens (claude)")