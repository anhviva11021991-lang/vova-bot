import os
import random
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# --- CẤU HÌNH HỆ THỐNG MẶC ĐỊNH ---
CONFIG = {
    "lever": 25,
    "mode": "Cross",
    "target_roe": 7.5,       # Mức chốt lời trung bình từ 5% - 10%
    "daily_target": 50,      # Chỉ tiêu dòng tiền (20 - 100 USD)
    "selected_coins": ["BTC", "ETH", "SOL", "BNB"], # Chạy đa nhiệm các Coin sếp chọn
    "safe_mode": False,       # Cầu chì tự động ngắt kết nối API thật
    "paper_trading": True,   # Giai đoạn 1: Giả lập Paper Trading
    "owner_name": "Sếp",
    "bot_name": "VOVA",
    "voice_muted": False
}

# --- TRẠNG THÁI LINH VẬT VOVA & HIỆU SUẤT ---
VOVA_STATUS = {
    "exp": 150,              # Điểm kinh nghiệm thực tế
    "level": 2,              # Tiến hóa từ cấp 1 -> 10
    "form": "Mầm cây 🌱",     # Hình thái tiến hóa theo cấp
    "mood": "Hân hoan 😄",    # Trạng thái tâm trạng động
    "pnl_today": 35.5,       # Lợi nhuận ròng trong ngày (USD)
    "win_streak": 4,
    "lose_streak": 0,
    "total_trades_today": 28 # Tần suất vào lệnh cao (20 - 50 lần/ngày)
}

# 10 Cấp độ tiến hóa của Thần thú VOVA
EVOLUTION_STAGES = {
    1: {"name": "Trứng sơ khai 🥚", "min_exp": 0},
    2: {"name": "Mầm cây 🌱", "min_exp": 100},
    3: {"name": "Cáo nhỏ 🦊", "min_exp": 300},
    4: {"name": "Sói máy Cyber 🐺", "min_exp": 600},
    5: {"name": "Hổ lôi đình 🐯", "min_exp": 1000},
    6: {"name": "Phượng hoàng lửa 🦅", "min_exp": 1500},
    7: {"name": "Kỳ lân công nghệ 🦄", "min_exp": 2200},
    8: {"name": "Kim cang hộ pháp 🦍", "min_exp": 3000},
    9: {"name": "Thượng cổ Thần thú 🦁", "min_exp": 4000},
    10: {"name": "Thần Rồng AI Vĩ Đại 🐉", "min_exp": 5500}
}

# --- CƠ CHẾ CẬP NHẬT TIẾN HÓA / THOÁI HÓA ---
def update_vova_evolution(pnl_change):
    if pnl_change > 0:
        VOVA_STATUS["exp"] += int(pnl_change * 2)
        VOVA_STATUS["win_streak"] += 1
        VOVA_STATUS["lose_streak"] = 0
        VOVA_STATUS["mood"] = random.choice(["Hân hoan 😄", "Phấn khích 🚀", "Tự hào 😎"])
    else:
        VOVA_STATUS["exp"] = max(0, VOVA_STATUS["exp"] - int(abs(pnl_change) * 3))
        VOVA_STATUS["win_streak"] = 0
        VOVA_STATUS["lose_streak"] += 1
        VOVA_STATUS["mood"] = random.choice(["Mếu máo 😢", "Tức giận 😡", "Lo lắng 😨"])
    
    current_lvl = 1
    for lvl, stage in sorted(EVOLUTION_STAGES.items(), reverse=True):
        if VOVA_STATUS["exp"] >= stage["min_exp"]:
            current_lvl = lvl
            break
    
    VOVA_STATUS["level"] = current_lvl
    VOVA_STATUS["form"] = EVOLUTION_STAGES[current_lvl]["name"]

    if VOVA_STATUS["lose_streak"] >= 3 and not CONFIG["paper_trading"]:
        CONFIG["safe_mode"] = True
        CONFIG["paper_trading"] = True

# --- WEB UI INTERFACE (HTML5, ADVANCED CSS KEYFRAMES, JAVASCRIPT) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống Giao Dịch AI - VOVA Engine</title>
    <link href="https://jsdelivr.net" rel="stylesheet">
    <style>
        :root {
            --neon-blue: #00f3ff;
            --neon-green: #39ff14;
            --neon-pink: #ff007f;
            --bg-dark: #0a0e17;
            --card-bg: #131a26;
        }
        body {
            background-color: var(--bg-dark);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .neon-border {
            border: 1px solid var(--neon-blue);
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
        }
        .dashboard-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .vova-container {
            position: relative;
            width: 180px;
            height: 180px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .vova-avatar {
            font-size: 80px;
            z-index: 2;
            animation: floatAnimation 3s ease-in-out infinite, blinkAnimation 4s ease-in-out infinite;
        }
        .vova-glow {
            position: absolute;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            z-index: 1;
            animation: pulseGlow 2s infinite alternate;
        }
        @keyframes floatAnimation {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-12px) rotate(2deg); }
            100% { transform: translateY(0px) rotate(0deg); }
        }
        @keyframes blinkAnimation {
            0%, 90%, 100% { opacity: 1; }
            45%, 55% { opacity: 0.93; transform: scaleY(0.98); }
        }
        @keyframes pulseGlow {
            0% {
                box-shadow: 0 0 20px 5px rgba(0, 243, 255, 0.4), inset 0 0 15px rgba(0, 243, 255, 0.2);
                background: rgba(0, 243, 255, 0.05);
            }
            100% {
                box-shadow: 0 0 40px 15px rgba(255, 0, 127, 0.5), inset 0 0 25px rgba(255, 0, 127, 0.3);
                background: rgba(255, 0, 127, 0.1);
            }
        }
        .chart-container {
            background: #02060c;
            height: 250px;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: flex-end;
            padding: 10px;
            gap: 4px;
        }
        .candle {
            flex: 1;
            border-radius: 2px;
            position: relative;
            transition: all 0.3s ease;
        }
        .candle.bullish { background-color: var(--neon-green); }
        .candle.bearish { background-color: var(--neon-pink); }
        .status-badge {
            font-size: 0.85rem;
            padding: 4px 10px;
            border-radius: 20px;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom border-secondary">
            <div>
                <h2 class="text-info fw-bold m-0">VOVA AI QUANT FUTURES ENGINE v2.0</h2>
                <small class="text-muted">Hệ thống vận hành đám mây 24/7 bảo mật tuyệt đối</small>
            </div>
            <div class="text-end">
                <span class="badge bg-danger status-badge me-2" id="safeModeBadge">Cầu chì: Đóng</span>
                <span class="badge bg-warning text-dark status-badge" id="tradingModeBadge">Paper Trading (Giai đoạn 1)</span>
            </div>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div class="dashboard-card neon-border">
                    <h5 class="text-info mb-3">🛠️ Khu Vực Cấu Hình Của Sếp</h5>
                    <div class="mb-3">
                        <label class="form-label text-white-50">🔄 Quét Sóng Đa Coin (Đồng thời):</label>
                        <select class="form-select bg-dark text-white border-secondary" id="coinSelector" onchange="changeCoin()">
                            <option value="BTC" selected>Cặp đa nhiệm: BTC/USDT Futures</option>
                            <option value="ETH">Cặp đa nhiệm: ETH/USDT Futures</option>
                            <option value="SOL">Cặp đa nhiệm: SOL/USDT Futures</option>
                            <option value="BNB">Cặp đa nhiệm: BNB/USDT Futures</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label text-white-50 d-flex justify-content-between">
                            <span>🎯 Chỉ tiêu dòng tiền hằng ngày:</span>
                            <span class="text-info fw-bold" id="sliderVal">50 USD</span>
                        </label>
                        <input type="range" class="form-range" min="20" max="100" value="50" id="targetSlider" oninput="updateSlider(this.value)">
                    </div>
                    <div class="row g-2 mb-3">
                        <div class="col">
                            <label class="small text-white-50">Chế độ ký quỹ</label>
                            <input type="text" class="form-control form-control-sm bg-dark text-white text-center border-secondary" value="Cross" disabled>
                        </div>
                        <div class="col">
                            <label class="small text-white-50">Mức đòn bẩy</label>
                            <input type="text" class="form-control form-control-sm bg-dark text-white text-center border-secondary" value="25x (Ưu tiên)" disabled>
                        </div>
                    </div>
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-light btn-sm" onclick="toggleVoice()">🔊 Bật/Tắt Âm Thanh Linh Vật</button>
                        <button class="btn btn-outline-info btn-sm" onclick="renameMaster()">👤 Đổi Tên Chủ Nhân / Linh Vật</button>
                        <button class="btn btn-danger btn-sm fw-bold" onclick="triggerVoiceControl()">🎤 Nhấn Để Ra Lệnh Bằng Giọng Nói (AI)</button>
                    </div>
                </div>
            </div>

            <div class="col-md-4 text-center">
                <div class="dashboard-card border border-secondary">
                    <h5 class="text-warning mb-2" id="vovaName">Hệ Thống Linh Vật: VOVA</h5>
                    <div class="vova-container my-3">
                        <div class="vova-glow" id="vovaGlow"></div>
    et currentCoin = "BTC";
const vovaAvatars = {
1: "🥚", 2: "🌱", 3: "🦊", 4: "🐺", 5: "🐯",
6: "🦅", 7: "🦄", 8: "🦍", 9: "🦁", 10: "🐉"
};
function updateSlider(val) {
document.getElementById("sliderVal").innerText = val + " USD";
}
function changeCoin() {
currentCoin = document.getElementById("coinSelector").value;
generateFakeCandles();
document.getElementById("botSpeech").innerText = "Báo cáo Sếp, VOVA đã chuyển đa nhiệm thành công sang quét sóng dữ liệu cặp ${currentCoin}/USDT!";
}
function generateFakeCandles() {
const chart = document.getElementById("candleChart");
chart.innerHTML = "";
for(let i=0; i<16; i++) {
const candle = document.createElement("div");
const height = Math.floor(Math.random() * 160) + 40;
const isBullish = Math.random() > 0.45;
candle.className = candle ${isBullish ? 'bullish' : 'bearish'};
candle.style.height = ${height}px;
chart.appendChild(candle);
}
}
function toggleVoice() {
alert("Đã chuyển đổi trạng thái âm thanh chống ồn cho linh vật VOVA!");
}
function renameMaster() {
const newName = prompt("Nhập tên mới cho Linh vật VOVA hoặc cấu hình lại quyền sở hữu của Sếp:");
if(newName) {
document.getElementById("vovaName").innerText = "Hệ Thống Linh Vật: " + newName;
}
}
function triggerVoiceControl() {
alert("🎤 Đang kích hoạt Microphone Web UI... Hệ thống đang ghi âm lệnh tiếng Việt của Sếp để truyền thẳng dữ liệu phân tích tương quan vào lõi AI!");
}
setInterval(() => {
fetch('/api/status?coin=' + currentCoin)
.then(res => res.json())
.then(data => {
document.getElementById("vovaLevel").innerText = "Cấp " + data.level;
document.getElementById("vovaForm").innerText = data.form;
document.getElementById("vovaMood").innerText = data.mood;
document.getElementById("vovaExp").innerText = data.exp + " EXP";
document.getElementById("pnlToday").innerText = (data.pnl_today >= 0 ? "+" : "") + data.pnl_today.toFixed(2) + " USD";
document.getElementById("totalTrades").innerText = data.total_trades_today + " / Ngày";
document.getElementById("vovaAvatar").innerText = vovaAvatars[data.level] || "🌱";
if(data.safe_mode) {
document.getElementById("safeModeBadge").className = "badge bg-success status-badge";
document.getElementById("safeModeBadge").innerText = "Cầu chì: TỰ NGẮT KÍCH HOẠT AN TOÀN";
document.getElementById("tradingModeBadge").innerText = "Đã ngắt API thật -> Đang chạy Paper Trading học lại xu hướng";
document.getElementById("tradingModeBadge").className = "badge bg-danger text-white status-badge";
}
if(Math.random() > 0.6) {
generateFakeCandles();
}
});
}, 3000);
generateFakeCandles();



"""
@app.route('/')
def index():
return render_template_string(HTML_TEMPLATE)
@app.route('/api/status', methods=['GET'])
def get_status():
coin = request.args.get('coin', 'BTC')
pnl_change = random.choice([4.5, 8.2, -5.0, 12.0, -3.5, -15.0])
VOVA_STATUS["pnl_today"] += pnl_change
VOVA_STATUS["total_trades_today"] += 1
update_vova_evolution(pnl_change)
return jsonify({
"exp": VOVA_STATUS["exp"],
"level": VOVA_STATUS["level"],
"form": VOVA_STATUS["form"],
"mood": VOVA_STATUS["mood"],
"pnl_today": VOVA_STATUS["pnl_today"],
"total_trades_today": VOVA_STATUS["total_trades_today"],
"safe_mode": CONFIG["safe_mode"],
"paper_trading": CONFIG["paper_trading"]
})
if name == 'main':
app.run(host='0.0.0.0', port=5000, debug=False)                    
                        <div class="vova-avatar" id="vovaAvatar">🌱</div>
                    </div>
                    <div class="row text-start mt-2 g-2">
