import re

def writing_quality(text):
    if not text:
        return 0

    # Count sentences
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip() != ""])

    # Count words
    words = text.split()
    word_count = len(words)

    if sentence_count == 0:
        return 0

    avg_sentence_length = word_count / sentence_count

    # Simple scoring logic
    if avg_sentence_length > 20:
        score = 85
    elif avg_sentence_length > 12:
        score = 75
    elif avg_sentence_length > 8:
        score = 65
    else:
        score = 50

    return score