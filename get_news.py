import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(topic):
    search_query = topic.replace("?", "").replace("Will ", "")[:100]

    url = "https://newsapi.org/v2/everything"
    params = {
        "q":        search_query,
        "sortBy":   "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey":   NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        articles = response.json().get("articles", [])

        if not articles:
            return "No recent news found."

        lines = []
        for article in articles:
            title = article.get("title", "").strip()
            date  = article.get("publishedAt", "")[:10]
            if title and "[Removed]" not in title:
                lines.append(f"- {title} ({date})")

        return "\n".join(lines)

    except Exception as e:
        return f"Could not fetch news: {e}"


if __name__ == "__main__":
    topic = "Federal Reserve interest rate 2026"
    print(f"Searching news for: {topic}\n")
    print(get_news(topic))