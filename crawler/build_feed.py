import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from sources.idownloadcoupon import scrape_idownloadcoupon
from sources.coursejoiner import scrape_coursejoiner
from sources.courson import scrape_courson
from sources.realdiscount import scrape_realdiscount

VN_TZ = timezone(timedelta(hours=7))
OUT_DIR = Path("public/udemy/v2")


def slug_from_udemy_url(url: str) -> str | None:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "course":
        return parts[1]
    return None


def coupon_from_url(url: str) -> str | None:
    qs = parse_qs(urlparse(url).query)
    return qs.get("couponCode", [None])[0]


def normalize_item(item: dict) -> dict | None:
    url = item.get("url", "").strip()

    if "udemy.com/course/" not in url:
        return None

    slug = slug_from_udemy_url(url)
    if not slug:
        return None

    coupon = coupon_from_url(url)

    return {
        "title": item.get("title", "").strip() or slug,
        "url": url,
        "source": item.get("source", "unknown"),
        "slug": slug,
        "couponCode": coupon,
    }


def main():
    now = datetime.now(VN_TZ)
    stamp = now.strftime("%Y-%m-%d-%H-%M")

    raw_items = []
    source_stats = {}

    scrapers = [
        scrape_idownloadcoupon,
        scrape_coursejoiner,
        scrape_courson,
        scrape_realdiscount,
    ]

    for scraper in scrapers:
        name = scraper.__name__.replace("scrape_", "")
        try:
            items = scraper()
            raw_items.extend(items)
            source_stats[name] = len(items)
            print(f"{name}: {len(items)} raw items")
        except Exception as e:
            source_stats[name] = f"failed: {e}"
            print(f"Source failed: {name}: {e}")

    courses_with_coupon = []
    free_courses = []
    seen = set()

    for raw in raw_items:
        item = normalize_item(raw)
        if not item:
            continue

        key = item["slug"] + "|" + str(item.get("couponCode"))
        if key in seen:
            continue
        seen.add(key)

        if item.get("couponCode"):
            courses_with_coupon.append(item)
        else:
            free_courses.append(item)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "version": 2,
        "generatedAt": now.isoformat(),
        "coursesWithCoupon": courses_with_coupon,
        "freeCourses": free_courses,
        "stats": {
            "raw": len(raw_items),
            "withCoupon": len(courses_with_coupon),
            "free": len(free_courses),
            "sources": source_stats,
        },
    }

    data_file = f"{stamp}.json"

    (OUT_DIR / data_file).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (OUT_DIR / "latest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    meta = {
        "version": 2,
        "lastSynced": stamp,
        "dataFile": data_file,
        "generatedAt": now.isoformat(),
        "sources": ["idownloadcoupon", "coursejoiner", "courson", "realdiscount"],
    }

    (OUT_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(data["stats"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
