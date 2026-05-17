import requests


def scrape_realdiscount():
    items = []

    url = "https://cdn.real.discount/api/courses?page=1&limit=500&sortBy=sale_start&store=Udemy&freeOnly=true"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.real.discount/",
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        data = r.json()
    except Exception:
        return items

    for item in data.get("items", []):
        if item.get("store") == "Sponsored":
            continue

        course_url = item.get("url")
        title = item.get("name", "")

        if course_url and "udemy.com/course/" in course_url:
            items.append({
                "title": title,
                "url": course_url,
                "source": "realdiscount",
            })

    return items
