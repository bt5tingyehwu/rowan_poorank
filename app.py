from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 允許跨域（Unity / 網頁前端都能存取）

LEADERBOARD_FILE = "leaderboard.json"
CLEAR_TOKEN = "rowan123"  # 用來重設榜單


def load_leaderboard():
    """讀取排行榜資料，若檔案不存在或壞掉，就回傳空 list。"""
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_leaderboard(data):
    """儲存排行榜資料到 JSON 檔。"""
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/api/submit-run", methods=["POST"])
def submit_run():
    """
    接收 Unity 上傳的成績 JSON，格式預期：
    {
        "playerName": "肉丸",
        "runId": "2025-11-24 23:59:25",
        "totalTime": 46.72,
        "missionTimes": [... 11 個 float ...],
        "allHiddenCleared": true
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    required = ["playerName", "runId", "totalTime", "missionTimes", "allHiddenCleared"]
    for key in required:
        if key not in data:
            return jsonify({"error": f"Missing field: {key}"}), 400

    leaderboard = load_leaderboard()

    entry = {
        "id": len(leaderboard) + 1,
        "playerName": data["playerName"],
        "runId": data["runId"],
        "totalTime": float(data["totalTime"]),
        "missionTimes": data["missionTimes"],
        "allHiddenCleared": bool(data["allHiddenCleared"])
    }

    leaderboard.append(entry)
    save_leaderboard(leaderboard)

    return jsonify({"status": "ok", "entryId": entry["id"]})


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """
    取得排序後的排行榜。
    回傳格式為 list：
    [
      {
        "id": 1,
        "playerName": "...",
        "runId": "...",
        "totalTime": 12.34,
        "missionTimes": [...],
        "allHiddenCleared": true
      },
      ...
    ]
    """
    leaderboard = load_leaderboard()
    # 依 totalTime 排序，小到大
    leaderboard_sorted = sorted(leaderboard, key=lambda x: x.get("totalTime", 9999999.0))
    return jsonify(leaderboard_sorted)


@app.route("/api/clear-leaderboard", methods=["GET"])
def clear_leaderboard():
    """
    清空排行榜（全部成績刪掉）。
    需帶上 ?token=XXX 才會成功。
    """
    token = request.args.get("token", "")

    if token != CLEAR_TOKEN:
        return jsonify({"error": "invalid token"}), 403

    # 直接覆寫為空陣列
    save_leaderboard([])

    return jsonify({"status": "ok", "message": "leaderboard cleared"})


if __name__ == "__main__":
    # 本機開發用，部署到 Render 時會改用 gunicorn 啟動
    app.run(host="0.0.0.0", port=5000, debug=True)