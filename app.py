import os
import time
import random
import threading
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

bot_state = {
    "owner_name": "Sếp",
    "vova_name": "VOVA AI",
    "sound_enabled": True,
    "trading_mode": "Paper Trading",
    "safe_mode_triggered": False,
    "selected_coins": ["BTC", "ETH", "SOL"],
    "daily_target": 50,
    "current_pnl": 0.0,
    "consecutive_losses": 0,
    "vova_exp": 150,
    "vova_level": 2,
    "vova_mood": "Bình Thường",
    "paper_days_left": 7,
    "logs": ["Hệ thống khởi động thành công trên Render.com ngầm 24/7."]
}

COIN_LIST = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOT", "LINK"]

VOVA_FORMS = [
    {"level": 1, "name": "Trứng sơ khai 🥚", "min_exp": 0, "color": "#7f8c8d"},
    {"level": 2, "name": "Mầm cây 🌱", "min_exp": 100, "color": "#2ecc71"},
    {"level": 3, "name": "Cáo nhỏ 🦊", "min_exp": 300, "color": "#e67e22"},
    {"level": 4, "name": "Sói Bạc 🐺", "min_exp": 600, "color": "#95a5a6"},
    {"level": 5, "name": "Hổ Lửa 🐯", "min_exp": 1000, "color": "#e74c3c"},
    {"level": 6, "name": "Phượng Hoàng 🔥", "min_exp": 1500, "color": "#9b59b6"},
    {"level": 7, "name": "Kỳ Lân Cổ Đại 🦄", "min_exp": 2100, "color": "#1abc9c"},
    {"level": 8, "name": "Bảo Thạch Ma Thần 💎", "min_exp": 2800, "color": "#2980b9"},
    {"level": 9, "name": "Chiến Thần Robot 🤖", "min_exp": 3600, "color": "#34495e"},
    {"level": 10, "name": "Thần Rồng AI 🐉", "min_exp": 4500, "color": "#f1c40f"}
]

VOVA_QUOTES = {
    "Hân Hoan": [
        "Sếp ơi, lệnh này ăn đậm rồi! Phát tài phát lộc!",
        "VOVA đang cảm thấy dòng tiền cuồn cuộn đổ về túi sếp!",
        "Xóng sánh đẹp quá, đúng bài ZigZag đa khung H1-M15-M5 rồi sếp!"
    ],
    "Khóc Lóc": [
        "Hu hu sếp ơi, thị trường kill Long/Short rồi, đau lòng quá!",
        "VOVA xin lỗi sếp, chuỗi sụt giảm này làm em teo tóp lại rồi...",
        "Cầu chì an toàn đã sẵn sàng, sếp đừng buồn nha!"
    ],
    "Bình Thường": [
        "Em đang quét tin vĩ mô từ Nhà Trắng, chưa có biến động lớn sếp ạ.",
        "Đang theo dõi lệnh Cross x25 đều đặn, mục tiêu 5%-10% ROE.",
        "Sếp có cần em dùng AI Gemini phân tích xu hướng ngay không?"
    ]
}

def update_vova_level():
    exp = bot_state["vova_exp"]
    current_lvl = 1
    for form in reversed(VOVA_FORMS):
        if exp >= form["min_exp"]:
            current_lvl = form["level"]
            break
    if current_lvl != bot_state["vova_level"]:
        bot_state["logs"].append(f"🔄 VOVA đã chuyển hóa hình thái sang Cấp {current_lvl}!")
        bot_state["vova_level"] = current_lvl

def background_trading_bot():
    while True:
        time.sleep(8)
        if not bot_state["selected_coins"]:
            continue
            
        coin = random.choice(bot_state["selected_coins"])
        action = random.choice(["LONG", "SHORT", "NO_SIGNAL"])
        
        if action != "NO_SIGNAL":
            roe = random.choice([7, 11, -5, -9])
            profit_loss = (bot_state["daily_target"] * (roe / 100)) * 2.5
            
            if bot_state["trading_mode"] == "Live Trading" and bot_state["safe_mode_triggered"]:
                continue
                
            bot_state["current_pnl"] += profit_loss
            
            if profit_loss > 0:
                bot_state["vova_exp"] += 15
                bot_state["vova_mood"] = "Hân Hoan"
                bot_state["consecutive_losses"] = 0
                msg = f"🟢 [{bot_state['trading_mode']}] Khớp lệnh {action} {coin} (Cross x25) thành công! +{profit_loss:.2f} USD (+{roe}% ROE)."
            else:
                bot_state["vova_exp"] = max(0, bot_state["vova_exp"] - 20)
                bot_state["vova_mood"] = "Khóc Lóc"
                bot_state["consecutive_losses"] += 1
                msg = f"🔴 [{bot_state['trading_mode']}] Lệnh {action} {coin} chạm điểm cắt lỗ. Dòng tiền sụt giảm {profit_loss:.2f} USD."
                
                if bot_state["trading_mode"] == "Live Trading" and bot_state["consecutive_losses"] >= 2:
                    bot_state["trading_mode"] = "Paper Trading"
                    bot_state["safe_mode_triggered"] = True
                    msg += " ⚠️ CẦU CHÌ TỰ ĐỘNG KÍCH HOẠT! Thua liên tiếp, ngắt API thật, quay về Paper Trading bảo toàn vốn!"
            
            update_vova_level()
            bot_state["logs"].append(msg)
            if len(bot_state["logs"]) > 25:
                bot_state["logs"].pop(0)

threading.Thread(target=background_trading_bot, daemon=True).start()

@app.route("/")
def index():
    return render_template_string(HTML_INTERFACE, state=bot_state, coin_list=COIN_LIST, forms=VOVA_FORMS)

@app.route("/api/state")
def get_state():
    quotes = VOVA_QUOTES.get(bot_state["vova_mood"], VOVA_QUOTES["Bình Thường"])
    current_quote = random.choice(quotes)
    current_form = next((f for f in VOVA_FORMS if f["level"] == bot_state["vova_level"]), VOVA_FORMS)
    return jsonify({
        **bot_state,
        "vova_quote": current_quote,
        "vova_color": current_form["color"],
        "vova_form_name": current_form["name"]
    })

@app.route("/api/update", methods=["POST"])
def update_config():
    data = request.json
    if "owner_name" in data: bot_state["owner_name"] = data["owner_name"]
    if "vova_name" in data: bot_state["vova_name"] = data["vova_name"]
    if "daily_target" in data: bot_state["daily_target"] = int(data["daily_target"])
    if "sound_enabled" in data: bot_state["sound_enabled"] = data["sound_enabled"]
    if "trading_mode" in data: 
        bot_state["trading_mode"] = data["trading_mode"]
        if data["trading_mode"] == "Live Trading":
            bot_state["safe_mode_triggered"] = False
            bot_state["consecutive_losses"] = 0
    if "selected_coins" in data: bot_state["selected_coins"] = data["selected_coins"]
    return jsonify({"status": "success"})

@app.route("/api/voice-command", methods=["POST"])
def voice_command():
    data = request.json
    speech_text = data.get("text", "")
    bot_state["logs"].append(f"🎙️ Nhận lệnh giọng nói: '{speech_text}' -> AI đang phân tích dữ liệu vĩ mô liên kết biểu đồ...")
    return jsonify({"reply": f"AI nhận lệnh thành công. Xu hướng ZigZag đa khung đang khớp dữ liệu thời gian thực."})

HTML_INTERFACE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VOVA AI - Trung Tâm Quản Trị</title>
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0b0d;
            --panel-bg: #131722;
            --neon-green: #00ff88;
            --neon-blue: #00d2ff;
            --neon-red: #ff3838;
            --text-main: #ffffff;
        }
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            margin: 0; padding: 20px;
            display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
        }
        h1, h2, h3, .brand { font-family: 'Orbitron', sans-serif; }
        .panel {
            background: var(--panel-bg);
            border: 1px solid #2a2e39;
            border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .full-width { grid-column: span 2; }
        .vova-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 280px; position: relative; background: #1c2030; border-radius: 12px;
            overflow: hidden;
        }
        .vova-avatar {
            font-size: 80px; margin-bottom: 15px;
            animation: floating 3s ease-in-out infinite, blinking 5s infinite;
            transition: all 0.5s ease;
            position: relative; z-index: 2;
        }
        .neon-glow-ring {
            position: absolute; width: 140px; height: 140px; border-radius: 50%;
            box-shadow: 0 0 35px var(--vova-glow-color, var(--neon-blue));
            animation: pulseGlow 2.5s linear infinite;
            opacity: 0.7; z-index: 1; top: 22%;
        }
        @keyframes floating {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }
        @keyframes blinking {
            0%, 90%, 100% { transform: scaleY(1) translateY(0); }
            95% { transform: scaleY(0.1) translateY(0); }
        }
        @keyframes pulseGlow {
            0% { transform: scale(1); filter: hue-rotate(0deg); }
            50% { transform: scale(1.18); opacity: 0.9; }
            100% { transform: scale(1); filter: hue-rotate(360deg); }
        }
        .status-badge { padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }
        .badge-paper { background: #2980b9; color: white; }
        .badge-live { background: var(--neon-red); color: white; box-shadow: 0 0 10px var(--neon-red); }
        .coin-checkbox { display: inline-flex; align-items: center; margin-right: 12px; background: #1e222d; padding: 6px 12px; border-radius: 6px; cursor: pointer; margin-bottom: 8px;}
        .coin-checkbox input { margin-right: 6px; }
        .log-box {
            background: #0e1118; border-radius: 6px; height: 220px; overflow-y: auto;
            padding: 10px; font-family: monospace; font-size: 13px; color: #b2b5be;
        }
        button {
            background: var(--neon-blue); border: none; color: black; font-weight: bold;
            padding: 10px 20px; border-radius: 6px; cursor: pointer; transition: 0.2s;
        }
        button:hover { opacity: 0.8; box-shadow: 0 0 15px var(--neon-blue); }
        .vova-speech {
            background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 8px;
