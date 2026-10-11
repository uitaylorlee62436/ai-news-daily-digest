import feedparser
import datetime
import os
from openai import OpenAI

# Config
RSS_FEEDS = ['https://hnrss.org/frontpage', 'https://feeds.bbci.co.uk/news/technology/rss.xml']
OUTPUT_DIR = './daily_digest'
client = OpenAI()  # uses OPENAI_API_KEY env


def fetch_articles(limit=20):
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            articles.append({'title': entry.title, 'link': entry.link})
    return articles


def select_hot_topics(articles, top_n=5):
    # Simple scoring by keyword importance, replace with LLM for better
    keywords = ['AI', 'open source', 'model', 'LLM', 'release']
    scored = []
    for a in articles:
        score = sum(1 for kw in keywords if kw.lower() in a['title'].lower())
        scored.append((score, a))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [a for _, a in scored[:top_n]]


def generate_summary(articles):
    prompt = "Summarize these headlines into a concise daily news digest:\n" + \
             "\n".join(f"- {a['title']}" for a in articles)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def write_digest(content, date):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{OUTPUT_DIR}/{date}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Daily Digest {date}\n\n{content}\n")
    print(f"Saved to {filename}")


def main():
    date = datetime.date.today().isoformat()
    articles = fetch_articles()
    hot = select_hot_topics(articles)
    if not hot:
        print("No articles found, skip.")
        return
    summary = generate_summary(hot)
    write_digest(summary, date)


if __name__ == '__main__':
    main()
