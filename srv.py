import telebot
import sqlite3
import threading
import os
import time
from flask import Flask, request, jsonify

# ======================
# НАСТРОЙКИ
# ======================
BOT_TOKEN = "8232353403:AAFJiq6cX-zWgDICtk3Wf4IJY_LIrqf43Z8"
DB_NAME = "vpn_bot.db"
ADMIN_PASSWORD = "2231231"  # ТВОЙ ПАРОЛЬ ДЛЯ АДМИНКИ

# ======================
# БАЗА ДАННЫХ (ЛОГИКА)
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
    except: return False

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, expire_date FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def update_user_date(user_id, new_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET expire_date = ? WHERE user_id = ?", (new_date, user_id))
    conn.commit()
    conn.close()

# ======================
# ТЕЛЕГРАМ БОТ (ИСПРАВЛЕННЫЙ ЦИКЛ)
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
    bot.reply_to(message, f"✅ Ты в базе!\n\nТвой ID для сайта:\n`{uid}`", parse_mode="Markdown")

def run_bot():
    """Бессмертный цикл опроса бота"""
    while True:
        try:
            print("Бот запущен...")
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Ошибка бота: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)

# ======================
# САЙТ (FLASK)
# ======================
app = Flask(__name__)

# ПРОВЕРКА ID (для защиты сайта)
@app.route("/check_id", methods=["POST"])
def check_id_endpoint():
    data = request.json
    user_id = data.get("user_id")
    if user_id and user_exists(user_id):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "ID не найден!"})

# ГЛАВНАЯ СТРАНИЦА (ТВОЙ ПОЛНЫЙ ДИЗАЙН)
@app.route("/")
def index():
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
            --bg-color: #020202; --card-bg: rgba(15, 15, 15, 0.8);
            --accent: #007AFF; --text-main: #ffffff; --text-dim: #86868b; --border: rgba(255, 255, 255, 0.1);
        }
        * { user-select: none; box-sizing: border-box; outline: none; }
        body, html { margin: 0; padding: 0; height: 100%; font-family: sans-serif; background: var(--bg-color); color: var(--text-main); display: flex; justify-content: center; align-items: center; overflow: hidden; }
        .orb { position: absolute; border-radius: 50%; filter: blur(100px); z-index: -1; opacity: 0.15; animation: move 20s infinite alternate; }
        .orb-1 { width: 400px; height: 400px; background: var(--accent); top: -10%; left: -5%; }
        @keyframes move { from { transform: translate(0, 0); } to { transform: translate(40px, 30px); } }
        #notification { position: fixed; top: -100px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 350px; background: rgba(28, 28, 30, 0.9); backdrop-filter: blur(25px); border: 1px solid var(--border); padding: 12px; border-radius: 20px; z-index: 2000; display: flex; align-items: center; gap: 12px; }
        .container { width: 100%; max-width: 420px; padding: 20px; opacity: 0; transform: scale(0.98); }
        .logo-text { font-size: 42px; font-weight: 800; text-align: center; margin-bottom: 30px; background: linear-gradient(180deg, #fff 0%, #888 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glass-card { background: var(--card-bg); backdrop-filter: blur(40px); border-radius: 35px; padding: 35px 25px; border: 1px solid var(--border); }
        .tariff-card { width: 100%; background: rgba(255,255,255,0.03); border: 1px solid var(--border); padding: 20px; border-radius: 24px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.3s; }
        .tariff-card:hover { border-color: var(--accent); transform: translateY(-3px); }
        .btn { width: 100%; padding: 20px; border: none; border-radius: 22px; background: var(--accent); color: #fff; font-size: 17px; font-weight: 700; cursor: pointer; transition: 0.3s; text-decoration: none; display: flex; justify-content: center; }
        input { width: 100%; padding: 20px; border-radius: 20px; border: 1px solid var(--border); background: rgba(255,255,255,0.06); color: #fff; text-align: center; margin-bottom: 20px; }
        .section { display: none; opacity: 0; flex-direction: column; align-items: center; }
        .active-section { display: flex; opacity: 1; }
        #welcome-overlay { position: fixed; inset: 0; background: #000; z-index: 1000; display: flex; justify-content: center; align-items: center; }
        .char { display: inline-block; opacity: 0; font-size: 42px; font-weight: 700; }
    </style>
</head>
<body>
    <div id="notification"><div style="background:var(--accent);width:30px;height:30px;border-radius:7px;"></div><div id="notif-text" style="font-size:13px;"></div></div>
    <div id="welcome-overlay"><div id="welcome-text"></div></div>
    <div class="orb orb-1"></div>
    <div class="container" id="main-container">
        <div class="logo-text">XexWay</div>
        <div class="glass-card">
            <div id="login-section" class="section active-section">
                <input type="text" id="user-id-input" placeholder="Введите ваш ID">
                <button class="btn" onclick="checkID()">Войти</button>
            </div>
            <div id="tariff-section" class="section">
                <div class="tariff-card" onclick="selectTariff('Standard', '85')"><span>Standard</span><b style="color:var(--accent)">85₽</b></div>
                <div class="tariff-card" onclick="selectTariff('Premium', '430')"><span>Premium</span><b style="color:var(--accent)">430₽</b></div>
            </div>
            <div id="payment-section" class="section">
                <h2 id="final-price"></h2>
                <a class="btn" href="https://t.me/XexWay_bot" target="_blank">Оплатить в боте</a>
                <p onclick="location.reload()" style="margin-top:20px; cursor:pointer; color:var(--text-dim)">← Назад</p>
            </div>
        </div>
    </div>
    <script>
        const text = "Привет, это XexWay";
        const wrapper = document.getElementById('welcome-text');
        text.split('').forEach(char => { const span = document.createElement('span'); span.textContent = char; span.className = 'char'; wrapper.appendChild(span); });
        window.onload = () => {
            const tl = gsap.timeline();
            tl.to(".char", { opacity: 1, stagger: 0.05, duration: 0.6 })
              .to("#welcome-overlay", { opacity: 0, duration: 0.8, delay: 0.5, onComplete: () => document.getElementById('welcome-overlay').style.display='none' })
              .to("#main-container", { opacity: 1, scale: 1, duration: 0.6 });
        };
        function showNotif(msg) {
            document.getElementById('notif-text').innerText = msg;
            gsap.to("#notification", { top: 20, duration: 0.5 });
            setTimeout(() => gsap.to("#notification", { top: -100, duration: 0.5 }), 3000);
        }
        function switchSection(id) {
            document.querySelector('.active-section').classList.remove('active-section');
            const next = document.getElementById(id);
            next.style.display = 'flex';
            setTimeout(() => next.classList.add('active-section'), 10);
        }
        async function checkID() {
            const val = document.getElementById('user-id-input').value;
            const res = await fetch('/check_id', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({user_id: val}) });
            const data = await res.json();
            if(data.success) { showNotif("Вход выполнен!"); switchSection('tariff-section'); }
            else showNotif("Ошибка: ID не найден!");
        }
        function selectTariff(n, p) { document.getElementById('final-price').innerText = p + " ₽"; switchSection('payment-section'); }
    </script>
</body>
</html>
    """

# ПАНЕЛЬ АДМИНА
@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    if request.args.get("pass") != ADMIN_PASSWORD:
        return "<h1>Доступ запрещен</h1>", 403
    
    if request.method == "POST":
        update_user_date(request.form.get("user_id"), request.form.get("expire_date"))

    users = get_all_users()
    rows = "".join([f"<tr><td>{u[0]}</td><td>{u[1]}</td><td><form method='POST'><input type='hidden' name='user_id' value='{u[0]}'><input name='expire_date' placeholder='Дата'><button>ОК</button></form></td></tr>" for u in users])
    return f"<h2>Админка XexWay</h2><table border='1'><tr><th>ID</th><th>Подписка</th><th>Изменить</th></tr>{rows}</table>"

# ======================
# ПРАВИЛЬНЫЙ ЗАПУСК
# ======================
if __name__ == "__main__":
    init_db()
    # Запускаем бота в отдельном потоке (threading)
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Запускаем сайт на порту, который выдаст Render или 5000 по умолчанию
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)