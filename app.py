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
# GIAO DIỆN WEB ĐỒ THỊ NẾN & LINH VẬT VOVA NEON
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VOVA AI Advanced Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #090d16; color: #f8fafc; padding: 15px; margin: 0; }
        .grid-layout { display: grid; grid-template-columns: 1fr; gap: 15px; max-width: 1200px; margin: auto; }
        @media (min-width: 768px) { .grid-layout { grid-template-columns: 350px 1fr; } }
        
        .panel { background: #131a26; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
        h2, h3 { color: #38bdf8; margin-top: 0; text-align: center; }
        
        /* Đồ họa Linh vật VOVA phát sáng theo Cấp độ và Tâm trạng */
        .vova-avatar-box { text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 15px; transition: all 0.5s ease; }
        .vova-icon { font-size: 70px; filter: drop-shadow(0 0 15px var(--glow-color)); animation: float 3s ease-in-out infinite; }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        .quote-box { background: #020617; padding: 10px; border-radius: 6px; font-style: italic; color: #cbd5e1; font-size: 13px; text-align: center; margin-top: 10px; border-left: 3px solid #38bdf8; }
        .data-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 14px; }
        .status-active { color: #4ade80; font-weight: bold; }
        
        .btn { display: block; width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; box-sizing: border-box; }
        .btn:hover { background: #0369a1; }
        .btn-test { background: #22c55e; margin-top: 15px; }
        .btn-test:hover { background: #16a34a; }
        
        /* Hộp đồ thị TradingView */
        .chart-container { height: 500px; min-height: 400px; width: 100%; border-radius: 12px; overflow: hidden; }
        .log-box { background: #020617; color: #a7f3d0; padding: 10px; border-radius: 6px; font-family: monospace; max-height: 120px; overflow-y: auto; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>

    <div class="grid-layout">
        <!-- CỘT TRÁI: THÔNG TIN LINH VẬT VOVA -->
        <div class="panel">
            <h2>🤖 ĐIỀU KHIỂN BOT AI</h2>
            
            <!-- Vùng hình ảnh Linh vật VOVA biến hình phát sáng -->
            <div class="vova-avatar-box" style="--glow-color: {{ color }}; background: rgba({{ rgb }}, 0.1); border: 1px solid {{ color }};">
                <div class="vova-icon">{{ icon }}</div>
                <div style="font-weight: bold; margin-top: 10px; color: {{ color }}; text-shadow: 0 0 8px {{ color }};">{{ form }}</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">Tâm trạng: {{ state.mood }}</div>
            </div>

            <div class="quote-box">
                💬 <b>VOVA nói:</b> "{{ quote }}"
            </div>

            <div style="margin-top: 15px;">
                <div class="data-row"><span>💵 Vốn giả lập:</span><span style="color: #f59e0b; font-weight:bold;">{{ state.paper_balance|round(2) }} USD</span></div>
                <div class="data-row"><span>⭐ Cấp tiến hóa:</span><span>Cấp {{ state.level }}/10</span></div>
                <div class="data-row"><span>🔥 Kinh nghiệm (EXP):</span><span>{{ state.exp }} EXP</span></div>
                <div class="data-row"><span>🟢 Trạng thái hệ thống:</span><span class="status-active">ONLINE</span></div>
            </div>

            <a href="/test-tele" class="btn btn-test">⚡ Thử Gửi Tin Telegram Khẩn Cấp</a>

            {% if test_result %}
            <div style="background: #451a03; padding: 10px; border-radius: 6px; margin-top: 10px; font-size:12px; border-left: 3px solid #f97316;">
                ⚠️ <b>Kết quả mạng:</b> {{ test_result }}
            </div>
            {% endif %}

            <h4 style="margin-bottom: 5px; color: #94a3b8;">📋 Nhật ký (Logs):</h4>
            <div class="log-box">
                {% for log in state.logs[::-1] %}
                    <div>[{{ loop.index }}] {{ log }}</div>
                {% endfor %}
            </div>
        </div>

        <!-- CỘT PHẢI: ĐỒ THỊ NẾN BINANCE TIÊN TIẾN -->
        <div class="panel" style="padding: 10px;">
            <h3 style="margin-bottom: 10px;">📊 BIỂU ĐỒ NẾN THẬT BINANCE FUTURES (BTCUSDT)</h3>
            <div class="chart-container">
                <!-- Mã Widget tích hợp đồ thị TradingView nhúng trực tiếp -->
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
    
    # Logic tính toán biến hình linh vật động theo Cấp độ (Level)
    lv = state.get("level", 1)
    if lv <= 2:
        icon, form, color, rgb = "🥚", "Trứng Sơ Khai Neon", "#a8a29e", "168,162,158"
    elif lv <= 4:
        icon, form, color, rgb = "🌱", "Mầm Cây Điện Tử", "#22c55e", "34,197,94"
    elif lv <= 6:
        icon, form, color, rgb = "🦊", "Cáo Nhỏ Công Nghệ", "#f97316", "249,115,22"
    elif lv <= 8:
        icon, form, color, rgb = "🦂", "Hổ Cáp Cyberpunk", "#e11d48", "225,29,72"
    else:
        icon, form, color, rgb = "🐉", "Thần Rồng AI Hủy Diệt", "#a855f7", "168,85,247"
        
    # Logic câu thoại tiếng Việt theo Tâm trạng (Mood)
    mood = state.get("mood", "Bình thường")
    quotes = {
        "Hân hoan 🎉": ["Xanh sàn rồi! Vào thêm lệnh nữa không sếp?", "Tiền về như nước, VOVA sắp hóa rồng rồi sếp ơi!"],
        "Bình thường": ["Thị trường chạy ổn, em đang quét sóng ZigZag nhé.", "Hệ thống bám sát nến thật Binance, sếp yên tâm."],
        "Lo lắng 📉": ["Thị trường quét râu ghê quá sếp ơi...", "Lệnh này thuật toán bị nhiễu rồi, em xin lỗi sếp nhé!"]
    }
    quote = random.choice(quotes.get(mood, quotes["Bình thường"]))
    
    if res and "Thành công" in res:
        state["mood"] = "Hân hoan 🎉"
        save_state(state)

    return render_template_string(
        HTML_TEMPLATE, state=state, test_result=res,
        icon=icon, form=form, color=color, rgb=rgb, quote=quote
    )

@web_app.route('/test-tele')
def test_tele():
    global test_status_cache
    state = get_state()
    
    now_str = datetime.now().strftime("%H:%M:%S")
    msg = f"⚡ *YÊU CẦU ĐÁ KÍCH TỪ GIAO DIỆN WEB EXPERT*\nThời gian: {now_str}\nVốn hiện tại: {state['paper_balance']} USD.\n\nĐường truyền từ Đám mây đến iPhone đã THÔNG SUỐT hoàn toàn!"
    
    status, response_text = send_telegram_direct(msg)
    
    log_msg = f"Ép gửi lúc {now_str}. Mã mạng: {status}"
    if "logs" not in state: state["logs"] = []
    state["logs"].append(log_msg)
    save_state(state)
    
    if status == 200:
        test_status_cache = "Thành công (Mã 200)! Telegram đã nhận lệnh. Sếp kiểm tra điện thoại ngay!"
    else:
        test_status_cache = f"Lỗi mạng (Mã {status})! Telegram phản hồi từ chối: {response_text}"
    return redirect(url_for('home'))

