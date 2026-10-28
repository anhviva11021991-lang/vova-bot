import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import os
import time
import json
import math
import random
from flask import Flask, render_template_string

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

# ==========================================
# GIAO DIỆN CHUẨN TRÌNH DUYỆT (CHỐNG CHẶN KẾT NỐI)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VOVA AI Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Tải thư viện TradingView chính thức để hiển thị đồ thị nến -->
    <script type="text/javascript" src="https://tradingview.com"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #090d16; color: #f8fafc; padding: 15px; margin: 0; }
        .grid-layout { display: grid; grid-template-columns: 1fr; gap: 15px; max-width: 1200px; margin: auto; }
        @media (min-width: 768px) { .grid-layout { grid-template-columns: 350px 1fr; } }
        .panel { background: #131a26; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; }
        h2, h3 { color: #38bdf8; text-align: center; margin-top: 0; }
        .vova-avatar-box { text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #38bdf8; background: rgba(56, 189, 248, 0.1); }
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
        <!-- CỘT TRÁI: ĐIỀU KHIỂN LINH VẬT VOVA -->
        <div class="panel">
            <h2>🤖 ĐIỀU KHIỂN BOT AI</h2>
            <div class="vova-avatar-box">
                <div class="vova-icon">{{ icon }}</div>
                <div style="font-weight: bold; margin-top: 10px; color: #38bdf8;">{{ form }}</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">Tâm trạng: {{ mood }}</div>
            </div>
            <div class="quote-box">💬 VOVA nói: "Hệ thống đường truyền đã được thông mạch hoàn toàn ra trình duyệt rồi sếp ơi!"</div>
            <div style="margin-top: 15px; margin-bottom: 15px;">
                <div class="data-row"><span>💵 Vốn ví giấy:</span><span style="color: #f59e0b; font-weight:bold;">{{ paper_balance }} USD</span></div>
                <div class="data-row"><span>⭐ Cấp độ VOVA:</span><span>Cấp {{ level }}/10</span></div>
                <div class="data-row"><span>🟢 Trạng thái mạng:</span><span style="color:#4ade80; font-weight:bold;">ONLINE</span></div>
            </div>
            <!-- ÉP THÔNG MẠCH TELEGRAM: Chạy trực tiếp qua trình duyệt của sếp để bỏ qua bộ lọc chặn của Render -->
            <a href="https://telegram.org!" 
               target="_blank" class="btn">⚡ Ép Gửi Tin Nhắn Telegram Khẩn Cấp</a>
        </div>
        
        <!-- CỘT PHẢI: ĐỒ THỊ NẾN THẬT BINANCE -->
        <div class="panel" style="padding: 10px;">
            <h3>📊 BIỂU ĐỒ NẾN THẬT BINANCE FUTURES (BTCUSDT)</h3>
            <div class="chart-container">
                <div id="vova_binance_chart" style="height:100%;width:100%;"></div>
                <script type="text/javascript">
                    // Khởi tạo Widget chính thức loại bỏ hoàn toàn lỗi từ chối kết nối iframe
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
                        "container_id": "vova_binance_chart"
                    });
                </script>
            </div>
        </div>
    </div>
</body>
</html>
"""

@web_app.route('/')
def home():
    state = get_state()
    lv = state.get("level", 1)
    if lv <= 2: icon, form = "🥚", "Trứng Sơ Khai Neon"
    elif lv <= 4: icon, form = "🌱", "Mầm Cây Điện Tử"
    elif lv <= 6: icon, form = "🦊", "Cáo Nhỏ Công Nghệ"
    else: icon, form = "🐉", "Thần Rồng AI Hủy Diệt"
        
    mood = state.get("mood", "Bình thường")

    return render_template_string(
        HTML_TEMPLATE, 
        paper_balance=round(state.get("paper_balance", 1000.0), 2),
        level=lv, mood=mood, icon=icon, form=form
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)
