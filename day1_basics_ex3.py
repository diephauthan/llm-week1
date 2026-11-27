from common import ask

text, tokens = ask("what is flank wear? anwser in 2 sentences")
print(text)
print(tokens)

text, tokens = ask("khi nào nên thay dao?", system = "answer briefly, in vietnamese")

print(text)
print("tổng token:", tokens["total"])