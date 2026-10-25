"""Coleta limitada e reutilizavel, sem anuncios, comentarios individuais ou Direct."""
from pathlib import Path
import argparse
import datetime as dt
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.instagram_analytics.client import AnalyticsError, InstagramAnalytics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dias", type=int, default=30)
    parser.add_argument("--ate", help="Ultimo dia incluido, YYYY-MM-DD; padrao: anteontem em Fortaleza.")
    parser.add_argument("--max-insights", type=int, default=10, help="Maximo de publicacoes com insights (0-20).")
    parser.add_argument("--insights-stories", type=int, default=1, help="Maximo de stories atuais com insights (0-3).")
    parser.add_argument("--saida", type=Path, default=ROOT / "tmp" / "instagram-analytics")
    args = parser.parse_args()
    if not 0 <= args.max_insights <= 20 or not 0 <= args.insights_stories <= 3:
        parser.error("Limites: 0-20 publicacoes e 0-3 stories com insights.")
    try:
        account = InstagramAnalytics().account_insights(args.dias, args.ate)
        end_date = (dt.date.fromisoformat(account["requested_window"]["end_exclusive"][:10]) - dt.timedelta(days=1)).isoformat()
        media = InstagramAnalytics().media(args.dias, end_date=end_date)
        stories = InstagramAnalytics().stories()
        result = {
            "identity": InstagramAnalytics().identity(),
            "permissions": InstagramAnalytics().permissions(),
            "account_insights": account, "media": media, "stories": stories,
            "media_insights": [InstagramAnalytics().media_insights(row["id"]) for row in media["data"][:args.max_insights]],
            "story_insights": [InstagramAnalytics().media_insights(row["id"]) for row in stories["data"][:args.insights_stories]],
            "limits": {"media_insights_max": args.max_insights, "story_insights_max": args.insights_stories,
                       "media_insights_omitted": max(0, len(media["data"])-args.max_insights),
                       "story_insights_omitted": max(0, len(stories["data"])-args.insights_stories)},
        }
    except AnalyticsError as error:
        parser.exit(1, str(error)+"\n")
    args.saida.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = args.saida / ("instagram-" + stamp + ".json")
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"file": str(dest), "posts": media["count"], "stories_now": stories["count"],
                      "window": account["requested_window"], "read_only": True}, ensure_ascii=True))


if __name__ == "__main__":
    main()
