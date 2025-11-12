# update_html.py (最終決戦コード)
import requests # requestsライブラリをインポート
import urllib.parse
from datetime import datetime, timezone, timedelta

# --- 設定項目 ---
GITHUB_USER_NAME = "ooaaoaoaoaoa" # ★書き換える
GITHUB_REPO_NAME = "pa"   # ★書き換える
PAGES_TO_FETCH = 3
# --------------

JST = timezone(timedelta(hours=9), 'JST')
# ニコニコのRSS URL
NICO_RSS_URL = "https://www.nicovideo.jp/tag/音MAD?sort=f&rss=2.0"
# 代理人（RSS変換サービス）のURL
RSS2JSON_API_URL = "https://api.rss2json.com/v1/api.json"
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
        .error-message {{ background-color: #fff7f7; color: #d8000c; padding: 20px; text-align: center; border: 1px solid #ffbaba; border-radius: 5px; }}
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
        {content}
        <div class="footer">
            最終更新: {update_time}
        </div>
    </div>
</body>
</html>
"""

def main():
    all_items = []
    for page_num in range(1, PAGES_TO_FETCH + 1):
        # ページ指定付きのRSS URLを作成
        paginated_rss_url = f"{NICO_RSS_URL}&page={page_num}"
        # 代理人サービスに渡すためのURLを作成
        params = {'rss_url': paginated_rss_url}
        
        try:
            print(f"Fetching page {page_num} via proxy...")
            # 代理人サービスにアクセス
            response = requests.get(RSS2JSON_API_URL, params=params, timeout=15)
            response.raise_for_status() # エラーがあればここで例外を発生させる
            data = response.json()
            
            # 結果を受け取ってリストに追加
            if data.get('status') == 'ok' and data.get('items'):
                all_items.extend(data['items'])
            else:
                print(f"No items found on page {page_num}. Stopping.")
                break # アイテムがなければループを抜ける
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break # エラーが発生したらループを抜ける
    
    print(f"Total {len(all_items)} items fetched.")

    if not all_items:
        content_html = '<div class="error-message"><strong>動画リストの取得に失敗しました。</strong><br>ニコニコ動画が一時的に不安定か、ネットワークの問題が発生した可能性があります。しばらくしてから手動で更新してみてください。</div>'
    else:
        content_list = []
        for item in all_items:
            title = item.get('title', 'タイトル不明')
            link = item.get('link', '#')
            # pubDateの形式 '2024-05-25 08:30:00' をdatetimeオブジェクトに変換
            try:
                # タイムゾーン情報がないので、JSTとみなして扱う
                pub_date = datetime.strptime(item.get('pubDate'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=JST)
                pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                pub_date_str = item.get('pubDate', '取得失敗')
            
            content_list.append(f'<li><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a><span class="pub-date">{pub_date_str}</span></li>')
        content_html = f'<ul>\n{"".join(content_list)}\n</ul>'

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
