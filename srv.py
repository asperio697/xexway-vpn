import telebot
import sqlite3
import threading
from flask import Flask, request, jsonify

# ======================
# НАСТРОЙКИ
# ======================
BOT_TOKEN = "8232353403:AAFJiq6cX-zWgDICtk3Wf4IJY_LIrqf43Z8"
DB_NAME = "vpn_bot.db"

# ======================
# БАЗА ДАННЫХ
# ======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            expire_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def user_exists(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except:
        return False

# ======================
# TELEGRAM BOT
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, expire_date) VALUES (?, ?)", 
                   (uid, "Нет активной подписки"))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ Регистрация успешна!\nТвой ID для сайта: `{uid}`", parse_mode="Markdown")

def run_bot():
    bot.infinity_polling()

# ======================
# САЙТ (FLASK)
# ======================
app = Flask(__name__)

# Маршрут для проверки ID через JavaScript (AJAX)
@app.route("/check_id", methods=["POST"])
def check_id_endpoint():
    data = request.json
    user_id = data.get("user_id")
    if user_id and user_exists(user_id):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "ID не найден в базе!"})

@app.route("/")
def index():
    # Твой крутой HTML шаблон
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XexWayVpn — Premium Access</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        :root {
            --bg-color: #020202;
            --card-bg: rgba(15, 15, 15, 0.8);
            --accent: #007AFF;
            --accent-glow: rgba(0, 122, 255, 0.4);
            --text-main: #ffffff;
            --text-dim: #86868b;
            --border: rgba(255, 255, 255, 0.1);
        }

        * { user-select: none; -webkit-user-select: none; box-sizing: border-box; outline: none; }

        body, html {
            margin: 0; padding: 0; height: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
            background: var(--bg-color); color: var(--text-main);
            display: flex; justify-content: center; align-items: center; overflow: hidden;
        }

        .orb {
            position: absolute; border-radius: 50%; filter: blur(100px); z-index: -1; opacity: 0.15;
            animation: move 20s infinite alternate ease-in-out;
        }
        .orb-1 { width: 400px; height: 400px; background: var(--accent); top: -10%; left: -5%; }
        .orb-2 { width: 500px; height: 500px; background: #5856d6; bottom: -10%; right: -5%; animation-delay: -5s; }
        @keyframes move { from { transform: translate(0, 0); } to { transform: translate(40px, 30px); } }

        #notification {
            position: fixed; top: -100px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 350px; background: rgba(28, 28, 30, 0.9);
            backdrop-filter: blur(25px); border: 1px solid var(--border);
            padding: 12px 18px; border-radius: 20px; z-index: 2000;
            display: flex; align-items: center; gap: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        }
        .notif-icon { width: 30px; height: 30px; background: var(--accent); border-radius: 7px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 10px; }

        #welcome-overlay {
            position: fixed; inset: 0; background: #000; z-index: 1000;
            display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        }
        .char { display: inline-block; opacity: 0; filter: blur(8px); transform: translateY(15px); font-size: 42px; font-weight: 700; letter-spacing: -1px; }
        .welcome-subtext { font-size: 16px; color: var(--text-dim); margin-top: 15px; opacity: 0; transform: translateY(10px); }

        .container { width: 100%; max-width: 420px; padding: 20px; opacity: 0; transform: scale(0.98); }

        .logo-text {
            font-size: 42px; font-weight: 800; text-align: center; margin-bottom: 30px;
            background: linear-gradient(180deg, #fff 0%, #888 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .glass-card {
            background: var(--card-bg); backdrop-filter: blur(40px);
            border-radius: 35px; padding: 35px 25px; border: 1px solid var(--border);
            box-shadow: 0 40px 100px rgba(0,0,0,0.7);
        }

        .tariff-card {
            width: 100%; background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px solid var(--border); padding: 22px;
            border-radius: 24px; margin-bottom: 15px;
            display: flex; justify-content: space-between; align-items: center;
            transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1); cursor: pointer;
        }
        .tariff-card:hover { border-color: var(--accent); transform: translateY(-3px) scale(1.02); background: rgba(0, 122, 255, 0.05); }
        .t-left { display: flex; flex-direction: column; gap: 4px; }
        .t-title { font-size: 18px; font-weight: 700; color: #fff; }
        .t-sub { font-size: 13px; color: var(--text-dim); }
        .t-price-box { background: rgba(0, 122, 255, 0.12); padding: 10px 16px; border-radius: 18px; border: 1px solid rgba(0, 122, 255, 0.2); }
        .t-price { font-size: 20px; font-weight: 850; color: var(--accent); }

        .payment-info { text-align: center; padding: 10px 0; }
        .payment-price { font-size: 56px; font-weight: 900; margin: 0; letter-spacing: -2px; color: #fff; }
        .payment-label { color: var(--text-dim); font-size: 15px; margin-bottom: 5px; }
        .payment-method-desc { color: var(--accent); font-size: 13px; margin-bottom: 30px; font-weight: 500; }

        .btn {
            width: 100%; padding: 20px; border: none; border-radius: 22px;
            background: var(--accent); color: #fff; font-size: 17px; font-weight: 700;
            cursor: pointer; box-shadow: 0 12px 30px var(--accent-glow); transition: 0.3s;
            text-decoration: none; display: flex; justify-content: center; align-items: center;
        }
        .btn:hover { filter: brightness(1.1); transform: translateY(-2px); }

        input {
            width: 100%; padding: 20px; border-radius: 20px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.06); color: #fff; text-align: center; margin-bottom: 20px; font-size: 16px;
        }

        .section { display: none; opacity: 0; flex-direction: column; align-items: center; }
        .active-section { display: flex; opacity: 1; }
        .back-link { margin-top: 25px; color: var(--text-dim); cursor: pointer; font-size: 14px; transition: 0.3s; }
        .back-link:hover { color: #fff; }
    </style>
</head>
<body>

<div id="notification">
    <div class="notif-icon" id="notif-status">XW</div>
    <div>
        <div id="notif-title" style="font-weight: 700; font-size: 13px;">XexWay VPN</div>
        <div id="notif-text" style="font-size: 12px; color: var(--text-dim);">Успешно</div>
    </div>
</div>

<div id="welcome-overlay">
    <div id="welcome-text"></div>
    <div class="welcome-subtext" id="welcome-sub">Лучший VPN для соц сетей</div>
</div>

<div class="orb orb-1"></div>
<div class="orb orb-2"></div>

<div class="container" id="main-container">
    <div class="logo-text">XexWay</div>
    <div class="glass-card">
        <div id="login-section" class="section active-section">
            <p style="color:var(--text-dim); font-size: 14px; margin-bottom: 25px;">Введите ваш ID</p>
            <input type="text" id="user-id-input" placeholder="Telegram ID">
            <button class="btn" onclick="checkID()">Войти</button>
        </div>

        <div id="tariff-section" class="section">
            <p style="color:var(--text-dim); margin-bottom: 25px;">Выберите план подписки</p>
            <div class="tariff-card" onclick="selectTariff('Standard', '85')">
                <div class="t-left">
                    <span class="t-title">Standard</span>
                    <span class="t-sub">1 месяц доступа</span>
                </div>
                <div class="t-price-box"><span class="t-price">85₽</span></div>
            </div>
            <div class="tariff-card" onclick="selectTariff('Premium', '430')">
                <div class="t-left">
                    <span class="t-title">Premium</span>
                    <span class="t-sub">6 месяцев доступа</span>
                </div>
                <div class="t-price-box"><span class="t-price">430₽</span></div>
            </div>
            <div class="back-link" onclick="logout()">Выйти</div>
        </div>

        <div id="payment-section" class="section">
            <div class="payment-info">
                <p id="selected-plan-name" class="payment-label"></p>
                <h2 id="final-price" class="payment-price"></h2>
                <p class="payment-method-desc">Оплата через Telegram-бот</p>
            </div>
            <a id="pay-button" class="btn" href="https://t.me/XexWay_bot" target="_blank">Купить в боте</a>
            <div class="back-link" onclick="switchSection('tariff-section')">← Изменить тариф</div>
        </div>
    </div>
</div>

<script>
    const text = "Привет, это XexWay";
    const wrapper = document.getElementById('welcome-text');
    text.split('').forEach(char => {
        const span = document.createElement('span');
        span.textContent = char === ' ' ? '\\u00A0' : char;
        span.className = 'char';
        wrapper.appendChild(span);
    });

    window.onload = () => {
        const tl = gsap.timeline();
        tl.to(".char", { opacity: 1, filter: "blur(0px)", y: 0, stagger: 0.04, duration: 0.7, ease: "power4.out" })
          .to("#welcome-sub", { opacity: 1, y: 0, duration: 0.8 }, "-=0.2")
          .to("#welcome-overlay", { opacity: 0, duration: 1, delay: 1.2, onComplete: () => { document.getElementById('welcome-overlay').style.display = 'none'; }})
          .to("#main-container", { opacity: 1, scale: 1, duration: 0.8 }, "-=0.4");
    };

    function showNotif(title, msg, isError = false) {
        document.getElementById('notif-title').innerText = title;
        document.getElementById('notif-text').innerText = msg;
        const icon = document.getElementById('notif-status');
        icon.style.background = isError ? "#FF3B30" : "#007AFF";
        
        gsap.to("#notification", { top: 20, duration: 0.6, ease: "back.out(1.7)" });
        setTimeout(() => { gsap.to("#notification", { top: -100, duration: 0.6 }); }, 3000);
    }

    function switchSection(id) {
        const curr = document.querySelector('.active-section');
        const next = document.getElementById(id);
        gsap.to(curr, { opacity: 0, y: 10, duration: 0.3, onComplete: () => {
            curr.classList.remove('active-section'); curr.style.display = 'none';
            next.style.display = 'flex';
            gsap.fromTo(next, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.4 });
            next.classList.add('active-section');
        }});
    }

    async function checkID() {
        const userId = document.getElementById('user-id-input').value;
        if(!userId) return;

        // Отправляем запрос на наш сервер Flask
        const response = await fetch('/check_id', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: userId})
        });
        const result = await response.json();

        if(result.success) {
            showNotif("Успешно", "Авторизация прошла!");
            switchSection('tariff-section');
        } else {
            showNotif("Ошибка", result.message, true);
        }
    }

    function selectTariff(name, price) {
        document.getElementById('selected-plan-name').innerText = "Тариф: " + name;
        document.getElementById('final-price').innerText = price + " ₽";
        switchSection('payment-section');
    }

    function logout() { location.reload(); }
</script>
</body>
</html>
"""

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(port=5000)  