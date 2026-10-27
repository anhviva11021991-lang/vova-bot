import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import os
import time
import json
import math
import random
import requests
from flask import Flask, render_template_string, request, redirect, url_for

web_app = Flask('')

# ==========================================
# CẤU HÌNH HỆ THỐNG
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
    """Hàm gửi tin nhắn và trả về kết quả lỗi chi tiết từ Telegram"""
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# ==========================================
# GIAO DIỆN WEB TRỰC QUAN (WEB DASHBOARD)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VOVA AI Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
        h2 { color: #38bdf8; text-align: center; margin-top: 0; }
        .card { background: #334155; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .status { font-weight: bold; color: #4ade80; }
        .btn { display: block; width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-align: center; text-decoration: none; margin-bottom: 10px; }
        .btn:hover { background: #0369a1; }
        .btn-test { background: #22c55e; }
        .btn-test:hover { background: #16a34a; }
        .log-box { background: #020617; color: #a7f3d0; padding: 10px; border-radius: 6px; font-family: monospace; max-height: 150px; overflow-y: auto; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 TRUNG TÂM ĐIỀU KHIỂN VOVA AI</h2>
        
        <div class="card">
            <p>💰 <b>Số dư ví giả lập:</b> {{ state.paper_balance }} USD</p>
            <p>⭐ <b>Cấp độ Linh vật:</b> Cấp {{ state.level }}</p>
            <p>🧠 <b>Tâm trạng VOVA:</b> {{ state.mood }}</p>
            <p>🟢 <b>Trạng thái mạng:</b> <span class="status">ONLINE (Đang chạy)</span></p>
        </div>

        <div class="card" style="border-left: 4px solid #22c55e;">
            <h3>🛡️ KIỂM TRA LỖI KẾT NỐI TELEGRAM</h3>
            <p style="font-size:13px; color:#cbd5e1;">Bấm nút dưới đây để ép hệ thống gửi 1 tin nhắn trực tiếp từ Đám mây về máy sếp nhằm kiểm tra lỗi:</p>
            <a href="/test-tele" class="btn btn-test">⚡ Ép Gửi Tin Nhắn Telegram Khẩn Cấp</a>
        </div>

        {% if test_result %}
        <div class="card" style="background: #451a03; border-left: 4px solid #f97316;">
            <h4>📊 Kết quả phản hồi từ mạng:</h4>
            <p style="font-family: monospace; font-size:12px;">{{ test_result }}</p>
        </div>
        {% endif %}

        <h3>📋 Nhật ký hệ thống ngầm (Logs):</h3>
        <div class="log-box">
            {% for log in state.logs[::-1] %}
                <div>[{{ loop.index }}] {{ log }}</div>
            {% endfor %}
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
    test_status_cache = None  # Xóa cache sau khi hiển thị
    return render_template_string(HTML_TEMPLATE, state=state, test_result=res)

@web_app.route('/test-tele')
def test_tele():
    global test_status_cache
    state = get_state()
    
    # Gửi tin nhắn kiểm thử hệ thống
    now_str = datetime.now().strftime("%H:%M:%S")
    msg = f"⚡ *YÊU CẦU ĐÁ KÍCH TỪ GIAO DIỆN WEB*\nThời gian kích hoạt: {now_str}\nTrạng thái ví: {state['paper_balance']} USD.\n\nNếu sếp thấy dòng này, đường truyền từ Đám mây đến iPhone đã THÔNG SUỐT hoàn toàn!"
    
    status, response_text = send_telegram_direct(msg)
    
    # Ghi nhận log vào hệ thống để sếp xem thử trên giao diện web
    log_msg = f"Bấm nút kiểm tra lúc {now_str}. Mã phản hồi mạng: {status}"
    if "logs" not in state: state["logs"] = []
    state["logs"].append(log_msg)
    save_state(state)
    
    if status == 200:
        test_status_cache = f"Thành công (Mã 200)! Telegram báo đã nhận lệnh. Sếp hãy kiểm tra điện thoại ngay!"
    else:
        test_status_cache = f"Lỗi (Mã {status})! Telegram phản hồi từ chối: {response_text}"
        
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)
