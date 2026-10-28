import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import os
import time
import json
import math
import random
import requests
from datetime import datetime
from flask import Flask, render_template_string, redirect, url_for, request

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
        "exp": 100,
        "mood": "Bình thường",
        "current_coin": "BINANCE:ZECUSDT.P"  # ƯU TIÊN: Cấu hình mặc định ban đầu là ZEC
    }

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

def send_telegram_direct(coin_name):
    t1 = "8923207528"
    t2 = "AAFQ789yaR6KzTTzH4sSnWSlW9_tuIJPf-4"
    full_token = t1 + ":" + t2
    
    url = f"https://telegram.org{full_token}/sendMessage"
    payload = {
        "chat_id": "2088141155",
        "text": f"🛰️ *VOVA AI THÔNG BÁO QUÉT SÓNG* 🛰️\n\n🎯 Thuật toán Scalping vừa kích hoạt quét dữ liệu đa khung thành công cho đồng: *{coin_name}*.\nTín hiệu đường truyền từ Đám mây đến iPhone của sếp an toàn 100%!",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# ==========================================
# GIAO DIỆN NÂNG CẤP ĐỒ HỌA HOẠT HÌNH ĐỘNG & BỘ CHỌN COIN
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VOVA AI Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Tải thư viện biểu đồ TradingView chính thức -->
    <script type="text/javascript" src="https://tradingview.com"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #070a13; color: #f8fafc; padding: 15px; margin: 0; }
        .grid-layout { display: grid; grid-template-columns: 1fr; gap: 15px; max-width: 1200px; margin: auto; }
        @media (min-width: 768px) { .grid-layout { grid-template-columns: 360px 1fr; } }
        .panel { background: #111827; padding: 20px; border-radius: 14px; border: 1px solid #1f2937; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
        h2, h3 { color: #38bdf8; text-align: center; margin-top: 0; text-shadow: 0 0 10px rgba(56,189,248,0.3); }
        
        /* HIỆU ỨNG HOẠT HỌA LINH VẬT VOVA CỬ ĐỘNG SINH ĐỘNG */
        .vova-avatar-box { text-align: center; padding: 25px; border-radius: 12px; margin-bottom: 15px; border: 2px solid {{ color }}; background: rgba({{ rgb }}, 0.08); box-shadow: 0 0 20px rgba({{ rgb }}, 0.2); position: relative; overflow: hidden; }
        
        .vova-icon { font-size: 80px; display: inline-block; filter: drop-shadow(0 0 20px {{ color }}); animation: vovaBreathing 2.5s ease-in-out infinite; }
        
        /* Hiệu ứng hào quang Neon RGB quét ngầm phía sau linh vật */
        .vova-avatar-box::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba({{ rgb }},0.15) 0%, transparent 60%); animation: neonPulse 4s linear infinite; z-index: 0; }
        .vova-icon, .vova-title, .vova-mood { position: relative; z-index: 1; }

        @keyframes vovaBreathing {
            0% { transform: translateY(0px) scale(1); filter: drop-shadow(0 0 15px {{ color }}); }
            50% { transform: translateY(-12px) scale(1.05); filter: drop-shadow(0 0 30px {{ color }}); }
            100% { transform: translateY(0px) scale(1); filter: drop-shadow(0 0 15px {{ color }}); }
        }
        @keyframes neonPulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .quote-box { background: #030712; padding: 12px; border-radius: 8px; font-style: italic; color: #e2e8f0; font-size: 13px; text-align: center; margin-top: 10px; border-left: 4px solid #38bdf8; }
        .data-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #374151; font-size: 14px; }
        
        /* THIẾT KẾ BỘ CHỌN COIN CHUYÊN NGHIỆP */
        .select-box { width: 100%; padding: 10px; background: #1f2937; color: white; border: 1px solid #4b5563; border-radius: 6px; font-weight: bold; font-size: 14px; margin-bottom: 15px; cursor: pointer; }
        .select-box:focus { border-color: #38bdf8; outline: none; }
        
        .btn { display: block; width: 100%; padding: 12px; background: #22c55e; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; box-sizing: border-box; transition: background 0.2s; }
        .btn:hover { background: #16a34a; }
        .chart-container { height: 530px; width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #1f2937; }
    </style>
</head>
<body>
    <div class="grid-layout">
        <!-- CỘT TRÁI: ĐIỀU KHIỂN & BỘ CHỌN COIN -->
        <div class="panel">
            <h2>🤖 ĐIỀU KHIỂN BOT AI</h2>
            
            <form action="/change-coin" method="POST">
                <label style="font-size: 13px; color: #94a3b8; display:block; margin-bottom: 5px;">🔥 Lựa chọn Sản phẩm giao dịch:</label>
                <select name="coin" class="select-box" onchange="this.form.submit()">
                    <option value="BINANCE:ZECUSDT.P" {% if current_coin == 'BINANCE:ZECUSDT.P' %}selected{% endif %}>🛡️ ZEC / Tether Perpetual (Ưu tiên)</option>
                    <option value="BINANCE:SOLUSDT.P" {% if current_coin == 'BINANCE:SOLUSDT.P' %}selected{% endif %}>⚡ SOL / Tether Perpetual (Ưu tiên)</option>
                    <option value="BINANCE:BTCUSDT.P" {% if current_coin == 'BINANCE:BTCUSDT.P' %}selected{% endif %}>🪙 BTC / Tether Perpetual</option>
                    <option value="BINANCE:ETHUSDT.P" {% if current_coin == 'BINANCE:ETHUSDT.P' %}selected{% endif %}>💎 ETH / Tether Perpetual</option>
                </select>
            </form>

            <div class="vova-avatar-box">
                <div class="vova-icon">{{ icon }}</div>
                <div class="vova-title" style="font-weight: bold; margin-top: 10px; color: {{ color }}; text-shadow: 0 0 8px {{ color }};">{{ form }}</div>
                <div class="vova-mood" style="font-size: 12px; color: #94a3b8; margin-top: 3px;">Tâm trạng: {{ mood }}</div>
            </div>
            
            <div class="quote-box">💬 VOVA nói: "{{ quote }}"</div>
            
            <div style="margin-top: 15px; margin-bottom: 15px;">
                <div class="data-row"><span>💵 Vốn ví giấy giả lập:</span><span style="color: #f59e0b; font-weight:bold;">{{ paper_balance }} USD</span></div>
                <div class="data-row"><span>⭐ Cấp độ VOVA:</span><span>Cấp {{ level }}/10</span></div>
                <div class="data-row"><span>🟢 Trạng thái mạng:</span><span style="color:#4ade80; font-weight:bold;">ONLINE (Tự động)</span></div>
            </div>
            
            <a href="/test-tele" class="btn">⚡ Ép Gửi Tin Nhắn Telegram Khẩn Cấp</a>
            
            {% if test_result %}
            <div style="background: #1e1b4b; padding: 12px; border-radius: 6px; margin-top: 10px; font-size:12px; border-left: 4px solid #6366f1;">
                🛰️ <b>Phản hồi mạng:</b> {{ test_result }}
            </div>
            {% endif %}
        </div>
        
        <!-- CỘT PHẢI: BIỂU ĐỒ HOẠT ĐỘNG CHUẨN XÁC NÉT CĂNG -->
        <div class="panel" style="padding: 10px;">
            <h3>📊 BIỂU ĐỒ NẾN THẬT BINANCE FUTURES</h3>
            <div class="chart-container" id="vova_expert_chart"></div>
            <script type="text/javascript">
                // Khởi tạo đồ thị động bám sát theo loại coin sếp lựa chọn
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "{{ current_coin }}",
                    "interval": "5",
                    "timezone": "Asia/Ho_Chi_Minh",
                    "theme": "dark",
                    "style": "1",
                    "locale": "vi",
                    "toolbar_bg": "#111827",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": false,
                    "container_id": "vova_expert_chart",
                    "studies": [
                        "RSI@tv-basicstudies"
                    ]
                });
            </script>
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
    if lv <= 2: icon, form, color, rgb = "🥚", "Trứng Sơ Khai Neon", "#a8a29e", "168,162,158"
    elif lv <= 4: icon, form, color, rgb = "🌱", "Mầm Cây Điện Tử", "#22c55e", "34,197,94"
    elif lv <= 6: icon, form, color, rgb = "🦊", "Cáo Nhỏ Công Nghệ", "#f97316", "249,115,22"
    else: icon, form, color, rgb = "🐉", "Thần Rồng AI Hủy Diệt", "#a855f7", "168,85,247"
        
    mood = state.get("mood", "Bình thường")
    coin_clean = state.get("current_coin", "ZECUSDT").split(":")[-1].replace(".P", "")
    quote = f"Em đang quét sóng thuật toán ZigZag cho đồng {coin_clean}. Sếp chọn đổi coin nào là biểu đồ tự nhảy theo đồng đó nhé!"

    return render_template_string(
        HTML_TEMPLATE, 
        paper_balance=round(state.get("paper_balance", 1000.0), 2),
        level=lv, mood=mood, icon=icon, form=form, color=color, rgb=rgb,
        quote=quote, current_coin=state.get("current_coin"), test_result=res
    )

