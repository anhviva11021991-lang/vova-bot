import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import os
import time
import json
import math
import random
import requests
from datetime import datetime
from flask import Flask, render_template_string, redirect, url_for

web_app = Flask('')

DATA_FILE = "vova_state.json"

def get_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "paper_balance": 1000.0,
        "level": 1,
        "mood": "Bình thường"
    }

def send_telegram_direct():
    # GIẢI PHÁP CHỐNG LỖI PORT: Tách chuỗi Token độc lập hoàn toàn để tránh lỗi 'not a valid host or port'
    t1 = "8923207528"
    t2 = "AAFQ789yaR6KzTTzH4sSnWSlW9_tuIJPf-4"
    full_token = t1 + ":" + t2
    
    url = "https://telegram.org" + full_token + "/sendMessage"
    payload = {
        "chat_id": "2088141155",
        "text": "🛰️ *KẾT NỐI KHẨN CẤP THÀNH CÔNG* 🛰️\n\nĐường truyền từ Đám mây đến iPhone của sếp đã thông suốt hoàn toàn, không còn lỗi dính chữ!",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# ==========================================
# GIAO DIỆN MỚI 2026: SỬ DỤNG WEB COMPONENTS ĐỘC LẬP
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VOVA AI Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #090d16; color: #f8fafc; padding: 15px; margin: 0; }
        .grid-layout { display: grid; grid-template-columns: 1fr; gap: 15px; max-width: 1200px; margin: auto; }
        @media (min-width: 768px) { .grid-layout { grid-template-columns: 350px 1fr; } }
        .panel { background: #131a26; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; }
        h2, h3 { color: #38bdf8; text-align: center; margin-top: 0; }
        .vova-avatar-box { text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
        .vova-icon { font-size: 70px; filter: drop-shadow(0 0 15px #38bdf8); }
        .quote-box { background: #020617; padding: 10px; border-radius: 6px; font-style: italic; color: #cbd5e1; font-size: 13px; text-align: center; margin-top: 10px; border-left: 3px solid #38bdf8; }
        .data-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 14px; }
        .btn { display: block; width: 100%; padding: 12px; background: #22c55e; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; box-sizing: border-box; }
        .btn:hover { background: #16a34a; }
        .chart-container { height: 500px; width: 100%; border-radius: 12px; overflow: hidden; }
    </style>
</head>
<body>
    <div class="grid-layout">
        <div class="panel">
            <h2>🤖 ĐIỀU KHIỂN BOT AI</h2>
            <div class="vova-avatar-box" style="background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8;">
                <div class="vova-icon">{{ icon }}</div>
                <div style="font-weight: bold; margin-top: 10px; color: #38bdf8;">{{ form }}</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">Tâm trạng: {{ mood }}</div>
            </div>
            <div class="quote-box">💬 VOVA nói: "{{ quote }}"</div>
            <div style="margin-top: 15px; margin-bottom: 15px;">
                <div class="data-row"><span>💵 Vốn ví giấy:</span><span style="color: #f59e0b; font-weight:bold;">{{ paper_balance }} USD</span></div>
                <div class="data-row"><span>⭐ Cấp độ VOVA:</span><span>Cấp {{ level }}/10</span></div>
                <div class="data-row"><span>🟢 Trạng thái mạng:</span><span style="color:#4ade80; font-weight:bold;">ONLINE</span></div>
            </div>
            <a href="/test-tele" class="btn">⚡ Ép Gửi Tin Nhắn Telegram Khẩn Cấp</a>
            {% if test_result %}
            <div style="background: #1e1b4b; padding: 10px; border-radius: 6px; margin-top: 10px; font-size:12px; border-left: 3px solid #6366f1;">
                🛰️ <b>Phản hồi mạng:</b> {{ test_result }}
            </div>
            {% endif %}
        </div>
        <div class="panel" style="padding: 10px;">
            <h3>📊 BIỂU ĐỒ NẾN THẬT BINANCE FUTURES (BTCUSDT)</h3>
            <div class="chart-container">
                <!-- ĐÃ NÂNG CẤP: Sử dụng nhúng mã nguồn thế hệ mới chạy thẳng trên trình duyệt không qua server -->
                <iframe src="https://tradingview.com" 
                        style="width: 100%; height: 100%; border: none; margin: 0; padding: 0;"></iframe>
            </div>
        </div>
    </div>
</body>
</html>
"""

test_status_cache = None

@web_app.route('/')
def home():
    global test_status_cache
    state = get_state()
    res = test_status_cache
    test_status_cache = None
    
    lv = state.get("level", 1)
    if lv <= 2: icon, form = "🥚", "Trứng Sơ Khai Neon"
    elif lv <= 4: icon, form = "🌱", "Mầm Cây Điện Tử"
    elif lv <= 6: icon, form = "🦊", "Cáo Nhỏ Công Nghệ"
    else: icon, form = "🐉", "Thần Rồng AI Hủy Diệt"
        
    mood = state.get("mood", "Bình thường")
    quote = "Hệ thống đã loại bỏ hoàn toàn mã lỗi 500 đường truyền. Sếp hãy kiểm tra biểu đồ và bấm nút kiểm tra lại nhé!"

    return render_template_string(
        HTML_TEMPLATE, 
        paper_balance=round(state.get("paper_balance", 1000.0), 2),
        level=lv, mood=mood, icon=icon, form=form, quote=quote, test_result=res
    )

@web_app.route('/test-tele')
def test_tele():
    global test_status_cache
    status, response_text = send_telegram_direct()
    
    if status == 200:
        test_status_cache = "Thành công (Mã 200)! Telegram thông mạch. Chuông điện thoại iPhone đang reo!"
    else:
        test_status_cache = f"Lỗi (Mã {status})! Chi tiết phản hồi: {response_text}"
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)
