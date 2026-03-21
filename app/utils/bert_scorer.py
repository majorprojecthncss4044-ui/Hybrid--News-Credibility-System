from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def get_bert_score(text):

    try:

        text = text.replace("\n", " ")

        result = classifier(text[:512])[0]

        score = result["score"]
        label = result["label"]

        if label == "POSITIVE":
            credibility_score = 60 + (score * 40)
        else:
            credibility_score = 60 - (score * 20)

        credibility_score = max(0, min(credibility_score, 100))

        return round(credibility_score, 2)

    except:
        return 60