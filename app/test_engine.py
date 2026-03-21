from utils.scoring_engine import hybrid_score

text = """Scientists confirm that drinking hot lemon water cures all types of cancer within 48 hours. Doctors are hiding this miracle treatment to protect pharmaceutical profits."""

url = "https://example.com/news"

result = hybrid_score(text, url)

for key, value in result.items():
    print(f"{key}: {value}")