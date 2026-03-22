import re

def writing_quality(text):
    if not text:
        return 0

    text = text.strip()

    # -------------------------------
    # Sentence Count
    # -------------------------------
    sentences = re.split(r'[.!?]', text)
    sentences = [s for s in sentences if s.strip() != ""]
    sentence_count = len(sentences)

    # -------------------------------
    # Word Count
    # -------------------------------
    words = text.split()
    word_count = len(words)

    if sentence_count == 0:
        return 0

    # -------------------------------
    # Average Sentence Length
    # -------------------------------
    avg_sentence_length = word_count / sentence_count

    # Base Score (structure-based)
    if avg_sentence_length > 20:
        score = 85
    elif avg_sentence_length > 12:
        score = 75
    elif avg_sentence_length > 8:
        score = 65
    else:
        score = 50

    # -------------------------------
    # Sensational Word Penalty
    # -------------------------------
    sensational_words = [
        "shocking", "unbelievable", "miracle", "exposed",
        "secret", "truth revealed", "you won't believe",
        "breaking!!!", "must watch", "100% proof"
    ]

    text_lower = text.lower()

    penalty_count = sum(word in text_lower for word in sensational_words)

    penalty = penalty_count * 5   # each word reduces score by 5

    # -------------------------------
    # Final Score
    # -------------------------------
    final_score = score - penalty

    # Clamp between 0–100
    final_score = max(0, min(100, final_score))

    return round(final_score, 2)