@echo off
REM テスト用バッチファイル
set PYTHONPATH=%cd%
echo 環境変数PYTHONPATHを設定しました: %PYTHONPATH%

REM モデル名の設定（必要に応じて変更）
set OLLAMA_MODEL=gemma3:12b
echo 使用するOllamaモデル: %OLLAMA_MODEL%

REM OllamaサーバーのベースURLを設定（デフォルト値）
set OLLAMA_API_URL=http://localhost:11434/api/chat
echo Ollama API URL: %OLLAMA_API_URL%

REM Pythonスクリプトを実行
echo テストを開始します...
python test_ollama.py

echo テスト完了
pause