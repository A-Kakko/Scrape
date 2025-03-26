import requests
import time
import sys

API_SERVER_URL = "http://192.168.1.10:11434/api/chat"


def main():
    headers = {"Content-Type": "application/json"}
    json = {
        "model": "gemma3:12b",
        "messages": [{
            "role": "user",
            "content": "Hello",
        }]
    }

    max_retries = 3
    retry_delay = 2  # 秒

    for attempt in range(max_retries):
        try:
            response = requests.post(API_SERVER_URL, headers=headers, json=json, timeout=30)
            response.raise_for_status()
            print(response.text)
            break  # 成功したらループを抜ける
            
        except requests.exceptions.Timeout:
            print(f"リクエストがタイムアウトしました。{attempt + 1}/{max_retries}回目")
            
        except requests.exceptions.ConnectionError:
            print(f"接続エラーが発生しました。サーバーに接続できません。{attempt + 1}/{max_retries}回目")
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTPエラーが発生しました: {e}")
            # HTTPエラーはリトライしない（400系や500系エラーなど）
            break
            
        except requests.exceptions.RequestException as e:
            print(f"リクエスト中にエラーが発生しました: {e}")
            
        # 最後の試行でなければ待機してリトライ
        if attempt < max_retries - 1:
            print(f"{retry_delay}秒後にリトライします...")
            time.sleep(retry_delay)
            # リトライごとに待機時間を増やす（バックオフ）
            retry_delay *= 2
        else:
            print("最大リトライ回数に達しました。処理を終了します。")
            sys.exit(1)


if __name__ == "__main__":
    main()