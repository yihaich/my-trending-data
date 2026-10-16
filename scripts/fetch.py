import json
import os
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def main():
    r = requests.get("https://github.com/trending?since=weekly",
                     headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for article in soup.select("article.Box-row")[:15]:
        a = article.select_one("h2 a")
        if not a:
            continue
        href = a.get("href")
        if not isinstance(href, str):
            continue

        name = "/".join(
            p.strip() for p in a.get_text(" ", strip=True).split("/") if p.strip()
        )
        url = "https://github.com" + href

        desc_el = article.select_one("p")
        desc = desc_el.get_text(" ", strip=True) if desc_el else ""

        gained_el = article.select_one("span.d-inline-block.float-sm-right")
        gained = gained_el.get_text(" ", strip=True) if gained_el else ""

        total = ""
        for a_tag in article.find_all("a"):
            tag_href = a_tag.get("href")
            if isinstance(tag_href, str) and tag_href.endswith("/stargazers"):
                total = a_tag.get_text(strip=True)
                break

        items.append({
            "repo": name,
            "url": url,
            "desc": desc,
            "stars": total,
            "currentPeriodStars": gained,
        })

    os.makedirs("data", exist_ok=True)
    with open("data/weekly.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(items)} items")


if __name__ == "__main__":
    main()
