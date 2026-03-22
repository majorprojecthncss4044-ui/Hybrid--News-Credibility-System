import requests
import os
API_KEY = "Your_Api_Key"

# ---------------------------------------
# Extract meaningful claim
# ---------------------------------------

def extract_claim(text):
    sentences = text.split(".")

    for sentence in sentences:
        sentence = sentence.strip()

        # choose meaningful sentence
        if len(sentence.split()) > 8:
            return sentence[:150]

    return text[:150]


# ---------------------------------------
# Fact Check Function
# ---------------------------------------

def check_fact_claim(text):

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    # Extract better claim
    claim = extract_claim(text)

    print("Fact Check Query:", claim)  # DEBUG

    params = {
        "query": claim,
        "key": API_KEY,
        "languageCode": "en"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "claims" not in data or len(data["claims"]) == 0:
            return 60, "No fact-check results found."

        claim_data = data["claims"][0]
        review = claim_data["claimReview"][0]

        rating = review.get("textualRating", "").lower()

        # ---------------------------------------
        # Improved scoring
        # ---------------------------------------

        if "true" in rating:
            return 95, "Claim verified as TRUE by fact-checkers."

        elif "false" in rating:
            return 10, "Claim verified as FALSE by fact-checkers."

        elif "misleading" in rating:
            return 30, "Claim is MISLEADING according to fact-checkers."

        elif "partly" in rating or "partial" in rating:
            return 60, "Claim is PARTIALLY true."

        else:
            return 70, f"Fact-check rating: {rating}"

    except Exception as e:
        print("Fact check error:", e)
        return 60, "Fact check unavailable."
