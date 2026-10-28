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
    "target_roe": 7.5,       
    "daily_target": 50,      
    "selected_coins": ["BTC", "ETH", "SOL", "BNB"], 
    "safe_mode": False,       
    "paper_trading": True,   
    "owner_name": "Sếp",
    "bot_name": "VOVA",
    "voice_muted": False
}

# --- TRẠNG THÁI LINH VẬT VOVA & HIỆU SUẤT ---
VOVA_STATUS = {
    "exp": 150,              
    "level": 2,              
    "form": "Mầm cây \U0001F331",     
    "mood": "Hân hoan \U0001F604",    
    "pnl_today": 35.5,       
    "win_streak": 4,
    "lose_streak": 0,
    "total_trades_today": 28 
}

# 10 Cấp độ tiến hóa của Thần thú VOVA
EVOLUTION_STAGES = {
    1: {"name": "Trứng sơ khai \U0001F95A", "min_exp": 0},
    2: {"name": "Mầm cây \U0001F331", "min_exp": 100},
    3: {"name": "Cáo nhỏ \U0001F98A", "min_exp": 300},
    4: {"name": "Sói máy Cyber \U0001F43A", "min_exp": 600},
    5: {"name": "Hổ lôi đình \U0001F42F", "min_exp": 1000},
    6: {"name": "Phượng hoàng lửa \U0001F985", "min_exp": 1500},
    7: {"name": "Kỳ lân công nghệ \U0001F984", "min_exp": 2200},
    8: {"name": "Kim cang hộ pháp \U0001F98D", "min_exp": 3000},
    9: {"name": "Thượng cổ Thần thú \U0001F941", "min_exp": 4000},
    10: {"name": "Thần Rồng AI Vĩ Đại \U0001F409", "min_exp": 5500}
}

def update_vova_evolution(pnl_change):
    if pnl_change > 0:
        VOVA_STATUS["exp"] += int(pnl_change * 2)
        VOVA_STATUS["win_streak"] += 1
        VOVA_STATUS["lose_streak"] = 0
        VOVA_STATUS["mood"] = random.choice(["Hân hoan \U0001F604", "Phấn khích \U0001F680", "Tự hào \U0001F60E"])
    else:
        VOVA_STATUS["exp"] = max(0, VOVA_STATUS["exp"] - int(abs(pnl_change) * 3))
        VOVA_STATUS["win_streak"] = 0
        VOVA_STATUS["lose_streak"] += 1
        VOVA_STATUS["mood"] = random.choice(["Mếu máo \U0001F622", "Tức giận \U0001F621", "Lo lắng \U0001F628"])
    
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

# --- WEB UI INTERFACE (CHUẨN HÓA KHÔNG LỖI CHUỖI) ---
HTML_TEMPLATE = """<!DOCTYPE html>
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
                        <div class="vova-avatar" id="vovaAvatar">🌱</div>
                    </div>
                    <div class="row text-start mt-2 g-2">
                        <div class="col-6"><span class="text-white-50 small">Cấp độ:</span> <strong class="text-info" id="vovaLevel">Cấp 2</strong></div>
                        <div class="col-6"><span class="text-white-50 small">Hình thái:</span> <strong class="text-success" id="vovaForm">Mầm cây 🌱</strong></div>
