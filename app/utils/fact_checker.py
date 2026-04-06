import requests

API_KEY = "YOUR_API_KEY"

def check_fact_claim(text):
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    params = {
        "query": text[:200],   # only send first 200 chars
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "claims" not in data:
            return 60, "No fact-check results found."

        claim = data["claims"][0]
        review = claim["claimReview"][0]

        rating = review.get("textualRating", "").lower()

        if "true" in rating:
            return 95, "Claim verified as TRUE by fact-checkers."

        elif "false" in rating:
            return 10, "Claim verified as FALSE by fact-checkers."

        else:
            return 50, f"Fact-check result: {rating}"

    except Exception:
        return 60, "Fact check unavailable."
