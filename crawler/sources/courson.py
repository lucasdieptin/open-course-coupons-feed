import requests


def scrape_courson(pages=10):
    items = []

    for page in range(1, pages + 1):
        try:
            r = requests.post(
                "https://courson.xyz/load-more-coupons",
                json={"filters": {}, "offset": (page - 1) * 30},
                timeout=30,
            )
            coupons = r.json().get("coupons", [])
        except Exception:
            continue

        if not coupons:
            break

        for item in coupons:
            id_name = item.get("id_name")
            coupon_code = item.get("coupon_code")
            title = item.get("headline", "").strip(' "')

            if id_name and coupon_code:
                items.append({
                    "title": title or id_name,
                    "url": f"https://www.udemy.com/course/{id_name}/?couponCode={coupon_code}",
                    "source": "courson",
                })

    return items
