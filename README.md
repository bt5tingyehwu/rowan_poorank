# 肉丸屎速通排行榜系統

這個 repo 包含：

- `app.py`: Flask 後端 API，接收 Unity 遊戲上傳的成績 JSON，並儲存在 `leaderboard.json`。
- `index.html`: 排行榜前端頁面，會從 API 取得資料並以表格顯示。
- `requirements.txt`: Python 依賴套件。
- `.gitignore`: 忽略虛擬環境與暫存檔。

## 本機開發

### 安裝依賴

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt