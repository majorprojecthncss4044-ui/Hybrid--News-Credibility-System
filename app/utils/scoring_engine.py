import joblib
import os
from urllib.parse import urlparse

from utils.bert_scorer import get_bert_score
from utils.fact_checker import check_fact_claim
from utils.writing_quality import writing_quality

print("Loaded Scoring Engine from:", __file__)

# --------------------------------
# Load ML Model + Vectorizer
# --------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

model_path = os.path.join(BASE_DIR, "models", "credibility_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)


# --------------------------------
# ML Score
# --------------------------------
def get_ml_score(text):
    vectorized = vectorizer.transform([text])
    prob = model.predict_proba(vectorized)[0][1]

    credibility_score = prob * 100
    label = 1 if prob >= 0.55 else 0

    return round(credibility_score, 2), label


# --------------------------------
# Source Credibility
# --------------------------------
trusted_sources = {
    "bbc.com": 95,
    "reuters.com": 95,
    "nytimes.com": 95,
    "theguardian.com": 90,
    "edition.cnn.com": 85,
    "thehindu.com": 90,
    "indianexpress.com": 85,
    "ndtv.com": 80,
    "aljazeera.com": 85,
    "apnews.com": 95,
    "washingtonpost.com": 90,
    "forbes.com": 85,
    "bloomberg.com": 95,
    "zeenews.india.com": 80,
    "aajtak.in": 80,
    "indiatoday.in": 85,
    "republicworld.com": 80,
    "abplive.com": 80,
    "hindustantimes.com": 88,
    "timesofindia.indiatimes.com": 85,
    "news18.com": 82,
    "financialexpress.com": 85,
    "eenadu.net": 85,
    "sakshi.com": 75,
    "tv9telugu.com": 80
}


def get_source_score(url):
    if not url:
        return 60

    try:
        domain = urlparse(url).netloc.lower()

        # remove common prefixes
        domain = domain.replace("www.", "").replace("m.", "")

        for trusted_domain, score in trusted_sources.items():
            if domain == trusted_domain or domain.endswith(trusted_domain):
                return score

        return 60

    except Exception:
        return 60


# =====================================
# DATASET PIPELINE (TEXT INPUT)
# ML + BERT
# =====================================
def dataset_score(text):

    text = text[:2000]

    # Scores
    ml_score, ml_label = get_ml_score(text)
    bert_score = round(get_bert_score(text), 2)

    # Hybrid score
    final_score = (
        0.9 * ml_score +
        0.1 * bert_score
    )

    final_score = round(max(0, min(100, final_score)), 2)

    # Credibility Level
    if final_score >= 75:
        level = "HIGH"
    elif final_score >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    # -------- FIXED EXPLANATION LOGIC --------
    explanation = []

    # ML explanation
    if ml_score >= 70:
        explanation.append(
            "Machine learning classifier predicts the article as credible based on learned patterns."
        )
    else:
        explanation.append(
            "Machine learning classifier predicts the article as less credible based on historical data patterns."
        )

    # BERT explanation
    if bert_score >= 70:
        explanation.append(
            "Semantic analysis shows strong contextual coherence and logical flow."
        )
    elif bert_score >= 40:
        explanation.append(
            "Semantic analysis shows moderate contextual consistency."
        )
    else:
        explanation.append(
            "Language patterns appear inconsistent with reliable journalism."
        )

    # Safety fallback (never empty)
    if not explanation:
        explanation.append(
            "The article lacks strong indicators of credibility."
        )

    return {
        "ML Score": ml_score,
        "BERT Score": bert_score,
        "Final Hybrid Score": final_score,
        "Credibility Level": level,
        "Explanation": " ".join(explanation)
    }


# =====================================
# LIVE NEWS PIPELINE (URL INPUT)
# Source + Writing + Fact Check
# =====================================
def live_news_score(text, url):

    text = text[:2000]

    source_score = get_source_score(url)
    writing_score = writing_quality(text)
    fact_score, fact_explanation = check_fact_claim(text)

    # ---------------------------------------
    # SMART PRIORITY WEIGHTING
    # ---------------------------------------
    if fact_score != 60:

        final_score = (
            0.85 * fact_score +
            0.10 * source_score +
            0.05 * writing_score
        )

        mode = "FACT_PRIORITY"

    elif source_score != 60:

        final_score = (
            0.70 * source_score +
            0.20 * writing_score +
            0.10 * fact_score
        )

        mode = "SOURCE_PRIORITY"

    else:

        final_score = (
            0.50 * source_score +
            0.25 * writing_score +
            0.25 * fact_score
        )

        mode = "BALANCED"

    # Clamp
    final_score = round(max(0, min(100, final_score)), 2)

    # ---------------------------------------
    # Credibility Level
    # ---------------------------------------
    if final_score >= 75:
        level = "HIGH"
    elif final_score >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    # ---------------------------------------
    # Explanation
    # ---------------------------------------
    explanation = []

    if source_score >= 85:
        explanation.append(
            "Article originates from a highly trusted news organization."
        )
    elif source_score < 70:
        explanation.append(
            "Article source has limited or unknown credibility."
        )

    if writing_score >= 80:
        explanation.append(
            "Writing style resembles professional journalism."
        )
    elif writing_score <= 50:
        explanation.append(
            "Sensational or exaggerated language detected."
        )

    explanation.append(fact_explanation)

    if mode == "FACT_PRIORITY":
        explanation.append(
            "Fact-check verification had the highest influence on the final score."
        )

    elif mode == "SOURCE_PRIORITY":
        explanation.append(
            "Trusted source credibility had the highest influence on the final score."
        )

    else:
        explanation.append(
            "Balanced scoring applied due to lack of strong signals."
        )

    return {
        "Source Score": source_score,
        "Writing Quality Score": writing_score,
        "Fact Check Score": fact_score,
        "Final Score": final_score,
        "Credibility Level": level,
        "Explanation": " ".join(explanation)
    }
