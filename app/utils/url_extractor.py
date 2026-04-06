from newspaper import Article


def extract_article(url):
    try:
        article = Article(url)

        article.download()
        article.parse()

        title = article.title
        text = article.text
        authors = article.authors
        publish_date = article.publish_date

        return title, text, authors, publish_date

    except Exception as e:
        print("Error extracting article:", e)
        return None, None, None, None
