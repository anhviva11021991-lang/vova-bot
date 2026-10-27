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

# ==========================================
# CẤU HÌNH HỆ THỐNG GIAO DỊCH
# ==========================================
TELEGRAM_TOKEN = "8923207528:AAFQ789yaR6KzTTzH4sSnWSlW9_tuIJPf-4"
CHAT_ID = "2088141155"
DATA_FILE = "vova_state.json"

def get_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "owner_name": "Sếp",
        "vova_name": "VOVA AI",
        "exp": 100,
        "level": 1,
        "mood": "Bình thường",
        "paper_balance": 1000.0,
        "logs": ["Hệ thống vừa thiết lập khởi tạo."]
    }

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def send_telegram_direct(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# ==========================================
# GIAO DIỆN WEB CHUẨN HÓA (CHỐNG LỖI COMPILER)
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
            <div style="background: #451a03; padding: 10px; border-radius: 6px; margin-top: 10px; font-size:12px; border-left: 3px solid #f97316;">
                ⚠️ <b>Kết quả mạng:</b> {{ test_result }}
            </div>
            {% endif %}
        </div>
        <div class="panel" style="padding: 10px;">
            <h3>📊 BIỂU ĐỒ NẾN THẬT BINANCE FUTURES (BTCUSDT)</h3>
            <div class="chart-container">
                <div class="tradingview-widget-container" style="height:100%;width:100%;">
                    <div id="tradingview_chart" style="height:100%;width:100%;"></div>
                    <script type="text/javascript" src="https://tradingview.com"></script>
                    <script type="text/javascript">
                    new TradingView.widget({
                        "autosize": true,
                        "symbol": "BINANCE:BTCUSDT.P",
                        "interval": "5",
                        "timezone": "Asia/Ho_Chi_Minh",
                        "theme": "dark",
                        "style": "1",
                        "locale": "vi",
                        "toolbar_bg": "#f1f3f6",
                        "enable_publishing": false,
                        "hide_side_toolbar": false,
                        "allow_symbol_change": true,
                        "container_id": "tradingview_chart"
                    });
                    </script>
                </div>
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
    quotes = {
        "Hân hoan 🎉": ["Xanh sàn rồi! Vào thêm lệnh nữa không sếp?", "Tiền về như nước, VOVA sắp hóa rồng rồi sếp ơi!"],
        "Bình thường": ["Thị trường chạy ổn, em đang quét sóng ZigZag nhé.", "Hệ thống bám sát nến thật Binance, sếp yên tâm."],
        "Lo lắng 📉": ["Thị trường quét râu ghê quá sếp ơi...", "Lệnh này thuật toán bị nhiễu rồi, em xin lỗi sếp nhé!"]
    }
    quote = random.choice(quotes.get(mood, quotes["Bình thường"]))

    # ĐÃ SỬA: Đưa toàn bộ biến ra ngoài, truyền tường minh chống lỗi biên dịch Render
    return render_template_string(
        HTML_TEMPLATE, 
        paper_balance=round(state.get("paper_balance", 1000.0), 2),
        level=lv, mood=mood, icon=icon, form=form, quote=quote, test_result=res
    )

@web_app.route('/test-tele')
def test_tele():
    global test_status_cache
    state = get_state()
    now_str = datetime.now().strftime("%H:%M:%S")
    msg = f"⚡ *YÊU CẦU ĐÁ KÍCH TỪ GIAO DIỆN WEB VỐN CỐ ĐỊNH*\nThời gian: {now_str}\nVốn hiện tại: {state['paper_balance']} USD.\n\nĐường truyền Đám mây đã THÔNG SUỐT hoàn toàn!"
    
    status, response_text = send_telegram_direct(msg)
    
    if status == 200:
        test_status_cache = "Thành công (Mã 200)! Telegram đã nhận lệnh. Sếp kiểm tra điện thoại ngay!"
    else:
        test_status_cache = f"Lỗi mạng (Mã {status})! Telegram phản hồi từ chối: {response_text}"
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)
