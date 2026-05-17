import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}


def uniq(seq):
    out = []
    seen = set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def scrape_coursejoiner(limit=80):
    items = []
    list_url = "https://coursejoiner.com/category/free-udemy/"

    try:
        r = requests.get(list_url, headers=HEADERS, timeout=30)
    except Exception:
        return items

    soup = BeautifulSoup(r.text, "html.parser")
    detail_links = []

    for a in soup.find_all("a", href=True):
        href = urljoin(list_url, a["href"])
        if "coursejoiner.com/free-udemy/" in href and "#respond" not in href:
            detail_links.append(href)

    for detail_url in uniq(detail_links)[:limit]:
        try:
            rr = requests.get(detail_url, headers=HEADERS, timeout=30)
        except Exception:
            continue

        ss = BeautifulSoup(rr.text, "html.parser")
        title = ss.title.get_text(" ", strip=True) if ss.title else detail_url
        title = title.replace(" - Course Joiner", "").strip()

        for a in ss.find_all("a", href=True):
            text = a.get_text(" ", strip=True).upper()
            href = urljoin(detail_url, a["href"])

            if "udemy.com/course/" in href and ("APPLY HERE" in text or "UDEMY" in href.upper()):
                items.append({
                    "title": title,
                    "url": href,
                    "source": "coursejoiner",
                })
                break

    return items
