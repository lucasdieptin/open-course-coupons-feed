import re
import requests
from html import unescape

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}


def clean_title(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title or "")
    return unescape(title).strip()


def scrape_idownloadcoupon(limit_pages=3):
    items = []

    for page in range(1, limit_pages + 1):
        api = f"https://idownloadcoupon.com/wp-json/wp/v2/product?product_cat=15&per_page=100&page={page}"

        try:
            r = requests.get(api, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                continue
            products = r.json()
        except Exception:
            continue

        if not products:
            break

        for product in products:
            title = clean_title(product.get("title", {}).get("rendered", ""))
            product_id = product.get("id")
            if not product_id:
                continue

            redeem = f"https://idownloadcoupon.com/udemy/{product_id}/"

            try:
                rr = requests.get(
                    redeem,
                    headers=HEADERS,
                    timeout=30,
                    allow_redirects=True,
                )
                final_url = rr.url
            except Exception:
                continue

            if "udemy.com/course/" not in final_url:
                continue

            items.append({
                "title": title,
                "url": final_url,
                "source": "idownloadcoupon",
            })

    return items
