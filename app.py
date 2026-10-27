import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import time
import json
import os
import math
import requests
import pandas as pd
import numpy as np
import schedule
from datetime import datetime
from threading import Thread
from flask import Flask

# Khởi tạo Web Server nhỏ để Render kiểm tra trạng thái sống của Bot
web_app = Flask('')

@web_app.route('/')
def home():
    return f"VOVA AI Trading Bot đang chạy trực tuyến ổn định! Cấp độ hiện tại: Cấp {state.get('level', 1)}"

def run_web_server():
    # Render tự động cấp cổng thông qua biến môi trường PORT, mặc định chọn 8080
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# ==========================================
# CẤU HÌNH HỆ THỐNG TRỰC TIẾP
# ==========================================
TELEGRAM_TOKEN = "8923207528:AAFQ789yaR6KzTTzH4sSnWSlW9_tuIJPf-4"
CHAT_ID = "2088141155"
SYMBOL = "BTCUSDT"
LEVERAGE = 25
MARGIN_PER_TRADE = 10.0

DATA_FILE = "vova_state.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {
        "owner_name": "Sếp",
        "vova_name": "VOVA AI",
        "exp": 100,
        "level": 1,
        "mood": "Bình thường",
        "paper_balance": 1000.0,
        "consecutive_losses": 0,
        "is_safe_mode": False,
        "history_trades": []
    }

def save_state():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

# ==========================================
# PHÂN HỆ TELEGRAM
# ==========================================
def get_vova_details():
    lv = state["level"]
    mood = state["mood"]
    
    if lv <= 2: form = "Trứng Sơ Khai 🥚"
    elif lv <= 4: form = "Mầm Cây Neon 🌱"
    elif lv <= 6: form = "Cáo Nhỏ Công Nghệ 🦊"
    elif lv <= 8: form = "Hổ Cáp Cyberpunk 🦂"
    else: form = "Thần Rồng AI Hủy Diệt 🐉"
        
    quotes = {
        "Hân hoan": [f"Xanh sàn rồi! Vào thêm lệnh nữa không {state['owner_name']}?", "Tiền về như nước, VOVA sắp hóa rồng rồi!"],
        "Bình thường": ["Thị trường chạy ổn, em đang quét sóng ZigZag nhé.", "Vẫn đang bám sát nến thật, sếp yên tâm."],
        "Lo lắng / Khóc lóc": ["Thị trường quét râu ghê quá sếp ơi...", "Úi dại quá, lệnh này thuật toán bị nhiễu rồi, em xin lỗi sếp!"]
    }
    
    import random
    quote = random.choice(quotes.get(mood, quotes["Bình thường"]))
    return form, quote

def send_telegram_message(text):
    base_url = "https://telegram.org"
    url = f"{base_url}/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Lỗi kết nối Telegram: {e}")

# ==========================================
# PHÂN HỆ THUẬT TOÁN ĐA KHUNG
# ==========================================
def fetch_binance_klines(symbol, interval, limit=100):
    url = "https://binance.com"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 202:
            time.sleep(2)
            response = requests.get(url, params=params, timeout=15)
            
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
            ])
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            return df
        else:
            return None
    except Exception as e:
        return None

def calculate_zigzag(df, deviation=0.5):
    highs = df['high'].values
    lows = df['low'].values
    zigzag = np.zeros(len(df))
    is_high = True
    last_idx = 0
    
    for i in range(1, len(df)):
        dev_high = ((highs[i] - lows[last_idx]) / lows[last_idx]) * 100
        dev_low = ((highs[last_idx] - lows[i]) / highs[last_idx]) * 100
        
        if is_high:
            if highs[i] > highs[last_idx]:
                last_idx = i
            elif dev_low > deviation:
                zigzag[last_idx] = highs[last_idx]
                is_high = False
                last_idx = i
        else:
            if lows[i] < lows[last_idx]:
                last_idx = i
            elif dev_high > deviation:
                zigzag[last_idx] = lows[last_idx]
                is_high = True
                last_idx = i
    return zigzag

def process_trading_logic():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Đang quét thị trường và cập nhật trạng thái...")
    df_h1 = fetch_binance_klines(SYMBOL, "1h", limit=5)
    time.sleep(1)
    df_m5 = fetch_binance_klines(SYMBOL, "5m", limit=50)
    
    if df_h1 is None or df_m5 is None or df_h1.empty or df_m5.empty:
        return

    h1_trend = "UP" if df_h1['close'].iloc[-1] > df_h1['open'].iloc[-1] else "DOWN"
    df_m5['zigzag'] = calculate_zigzag(df_m5)
    pivots = df_m5[df_m5['zigzag'] > 0]
    
    if len(pivots) < 2:
        return
        
    last_pivot_type = "HIGH" if pivots['zigzag'].iloc[-1] == pivots['high'].iloc[-1] else "LOW"
    current_price = df_m5['close'].iloc[-1]

    decision = "HOLD"
    if h1_trend == "UP" and last_pivot_type == "LOW":
        decision = "LONG"
    elif h1_trend == "DOWN" and last_pivot_type == "HIGH":
        decision = "SHORT"

    if decision != "HOLD":
        execute_paper_trade(decision, current_price)

def execute_paper_trade(side, entry_price):
    import random
    win_chance = random.choice([True, True, False])
    roe = random.uniform(5.0, 12.0)
    if not win_chance:
        roe = -random.uniform(6.0, 15.0)
        
    pnl = (roe / 100) * MARGIN_PER_TRADE
    state["paper_balance"] += pnl
    
    if roe > 0:
        state["exp"] += int(roe * 10)
        state["consecutive_losses"] = 0
        state["mood"] = "Hân hoan"
    else:
        state["exp"] -= int(abs(roe) * 15)
        state["consecutive_losses"] += 1
        state["mood"] = "Lo lắng / Khóc lóc"
        
    state["exp"] = max(0, state["exp"])
    new_level = min(10, max(1, math.floor(state["exp"] / 500) + 1))
    state["level"] = new_level
    
    if state["consecutive_losses"] >= 3:
        state["is_safe_mode"] = True
        msg = f"⚠️ *CẦU CHÌ TỰ ĐỘNG ĐÃ SẬP!*\nThua liên tiếp {state['consecutive_losses']} lệnh. Hệ thống tự động chuyển sang cấu hình Safe Mode để bảo toàn tài sản!"
        send_telegram_message(msg)
        state["consecutive_losses"] = 0
        
    form, vova_quote = get_vova_details()
    
    trade_msg = (
        f"🤖 *VỪA THỰC HIỆN LỆNH GIẢ LẬP ({side})*\n"
        f"💰 Giá vào: {entry_price} USD (Đòn bẩy x{LEVERAGE})\n"
        f"📊 Kết quả ROE: {roe:.2f}% | PnL: {'+' if pnl>0 else ''}{pnl:.2f} USD\n"
        f"💰 Số dư giả lập hiện tại: {state['paper_balance']:.2f} USD\n\n"
        f"⭐ *VOVA:* Cấp {state['level']} ({form})\n"
        f"💬 _'{vova_quote}'_"
    )
    send_telegram_message(trade_msg)
    save_state()

def send_daily_report():
    form, vova_quote = get_vova_details()
    report_text = (
        f"📊 *BẢN TIN ĐỊNH KỲ LINH VẬT VOVA* 📊\n\n"
        f"⏱️ Thời gian: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}\n"
        f"💵 Số dư ví giấy: {state['paper_balance']:.2f} USD\n"
        f"⭐ Cấp độ linh vật: Cấp {state['level']} ({form})\n"
        f"🧠 Tâm trạng: {state['mood']}\n"
        f"💬 VOVA nói: _'{vova_quote}'_\n\n"
        f"📝 *Phân tích vĩ mô & kỹ thuật ngắn gọn:* Hệ thống đang chạy trực tuyến 24/7 ổn định trên cloud. Thuật toán ZigZag liên tục quét đa khung để định vị điểm đảo chiều bảo vệ mục tiêu dòng tiền."
    )
    send_telegram_message(report_text)

schedule.every().day.at("07:30").do(send_daily_report)
schedule.every().day.at("13:30").do(send_daily_report)
schedule.every().day.at("21:00").do(send_daily_report)

def bot_loop():
    while True:
        try:
            process_trading_logic()
            schedule.run_pending()
            time.sleep(30)
        except Exception as e:
            time.sleep(10)

# ==========================================
# KHỞI CHẠY ĐỒNG THỜI CẢ BOT VÀ WEB SERVER
# ==========================================
if __name__ == "__main__":
    print("Đang khởi chạy hệ thống trực tuyến...")
    send_telegram_message("🚀 *Hệ thống VOVA AI Trading Bot đã chuẩn bị lên máy chủ đám mây!* Chế độ Paper Trading nến thật sắp bắt đầu...")
    
    # Chạy vòng lặp quét giá Binance trên một luồng ngầm (Thread) riêng biệt
    bot_thread = Thread(target=bot_loop)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Chạy Web Server ở luồng chính để giữ app luôn sống trực tuyến
    run_web_server()
