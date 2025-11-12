# update_html.py
import feedparser
from datetime import datetime, timezone, timedelta

# --- 設定項目 ---
# あなたのGitHubユーザー名とリポジトリ名に書き換えてください
GITHUB_USER_NAME = "ooaaoaoaoaoa"
GITHUB_REPO_NAME = "pa" 
PAGES_TO_FETCH = 3  # 取得したいページ数 (1ページ約30件)
# --------------

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9), 'JST')
RSS_URL = "https://www.nicovideo.jp/tag/音MAD?sort=f&rss=2.0"
ACTIONS_URL = f"https://github.com/{GITHUB_USER_NAME}/{GITHUB_REPO_NAME}/actions/workflows/main.yml"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>音MAD新着リスト</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif; margin: 1em; background-color: #f4f4f9; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 1.5em; }}
        h1 {{ font-size: 1.5em; color: #444; margin: 0; }}
        .update-button {{ display: inline-block; padding: 10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 0.9em; }}
        .update-button:hover {{ background-color: #218838; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background-color: #fff; margin-bottom: 10px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: transform 0.2s; }}
        li:hover {{ transform: translateY(-2px); }}
        a {{ text-decoration: none; color: #0066cc; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
        .pub-date {{ display: block; font-size: 0.8em; color: #777; margin-top: 5px; }}
        .footer {{ text-align: center; margin-top: 2em; font-size: 0.9em; color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>音MAD新着リスト</h1>
            <a href="{actions_url}" target="_blank" class="update-button">手動で更新</a>
        </div>
        <ul>
            {content}
        </ul>
        <div class="footer">
            最終更新: {update_time}
        </div>
    </div>
</body>
</html>
"""

def main():
    all_entries = []
    for page_num in range(1, PAGES_TO_FETCH + 1):
        paginated_url = f"{RSS_URL}&page={page_num}"
        print(f"Fetching page {page_num}...")
        feed = feedparser.parse(paginated_url)
        if not feed.entries:
            break
        all_entries.extend(feed.entries)
    
    print(f"Total {len(all_entries)} items fetched.")

    content_list = []
    for entry in all_entries:
        title = entry.title
        link = entry.link
        try:
            pub_date_utc = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            pub_date_jst = pub_date_utc.astimezone(JST).strftime('%Y-%m-%d %H:%M')
        except:
            pub_date_jst = "取得失敗"

        content_list.append(f'<li><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a><span class="pub-date">{pub_date_jst}</span></li>')
    
    content_html = "\n".join(content_list)
    update_time_str = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S JST')
    
    final_html = HTML_TEMPLATE.format(
        actions_url=ACTIONS_URL,
        content=content_html, 
        update_time=update_time_str
    )
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print("index.html generated successfully.")

if __name__ == "__main__":
    main()
