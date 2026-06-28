from flask import Flask, render_template_string, request, jsonify, send_from_directory, session, redirect, url_for
import requests
from datetime import datetime, timedelta
import os
import json
import uuid
from werkzeug.utils import secure_filename
import pytz

app = Flask(__name__)
app.secret_key = 'bab_al_rahma_secret_key_2026'

UPLOAD_FOLDER = 'uploads'
ADMIN_PASS = 'AAAAVSH8EHD BDOIDOHEVVSGUDIHDGHSIVXB BBXU8EIYWGBWI8DHKSHF6283883GRB8R8IEVVSBSV'
API_KEY_UPLOAD = '3fd6caa2e26d2b535c568e6616891b46'
SUDAN_TZ = pytz.timezone('Africa/Khartoum')
DATA_FILE = 'adhkar_data.json'
BROADCAST_MSG = {"text": "", "time": 0}
MISARI_IMAGE_URL = "https://i.ytimg.com/vi/1kO8o0QyL5g/maxresdefault.jpg"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

SURAH_NAMES = {1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة", 6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس", 11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر", 16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه", 21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان", 26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم", 31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر", 36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر", 41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية", 46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق", 51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن", 56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة", 61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق", 66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج", 71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة", 76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس", 81: "التكوير", 82: "الإنفطار", 83: "المطففين", 84: "الإنشقاق", 85: "البروج", 86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد", 91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين", 96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات", 101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل", 106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر", 111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"}

def load_adhkar():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_adhkar(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌙 باب الرحمة</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri+Quran:wght@400;700&family=Cairo:wght@700;900&display=swap" rel="stylesheet">
<style>
* {margin:0; padding:0; box-sizing:border-box}
body {background: #000; color: #fff; font-family: 'Cairo', sans-serif; padding: 15px;}
.container {max-width: 900px; margin: auto}
.logo {font-size: 42px; font-weight: 900; color: #ffd700; text-align: center; margin-bottom: 20px; text-shadow: 0 0 30px #ffd700;}
.card {background: #111; border: 3px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 20px;}
.card h2 {color: #ffd700; text-align: center; margin-bottom: 15px; font-size: 24px; font-weight: 900;}
.digital-clock {background: #000; border: 5px solid #00ff00; border-radius: 10px; padding: 30px; margin: 20px 0; text-align: center;}
.time-large {font-size: 80px; color: #00ff00; font-family: monospace; font-weight: 900; letter-spacing: 10px;}
.date-large {font-size: 24px; color: #ffaa00; margin-top: 10px; font-weight: 700;}
.today-day {font-size: 28px; color: #00ff00; margin-top: 10px; font-weight: 900; text-shadow: 0 0 15px #00ff00;}
.prayer-digital {background: #000; border: 4px solid #ff0000; border-radius: 8px; padding: 25px 15px; margin: 12px 0; text-align: center;}
.prayer-name {font-size: 22px; color: #ffd700; margin-bottom: 8px; font-weight: 900;}
.prayer-time {font-size: 56px; color: #ff0000; font-family: monospace; font-weight: 900; letter-spacing: 8px;}
select, input {width: 100%; padding: 14px; border-radius: 10px; border: 3px solid #d4af37; background: #1a1a1a; color: #ffd700; font-size: 18px; margin-bottom: 10px; font-weight: 700;}
.btn {width: 100%; background: linear-gradient(135deg, #ffd700, #ffaa00); color: #000; border: none; padding: 16px; font-size: 19px; font-weight: 900; border-radius: 10px; cursor: pointer; margin: 8px 0;}
.quran-text {font-family: 'Amiri Quran', serif; font-size: 32px; line-height: 3; color: #ffd700; text-align: center; padding: 20px; background: #0a0a0a; border-radius: 10px;}
.khutba-card {background: linear-gradient(135deg, #2d1a5d, #1a0f3d); border: 3px solid #ffd700; padding: 25px; border-radius: 15px; text-align: center; margin: 20px 0;}
.zikr-big {width: 100%; max-width: 500px; margin: 15px auto; display: block; border-radius: 15px; border: 4px solid #ffd700; box-shadow: 0 0 30px #ffd700; background: #222;}
.empty-zikr {text-align: center; color: #666; font-size: 18px; padding: 30px;}
.footer {text-align: center; padding: 30px; margin-top: 40px; border-top: 3px solid #333; color: #ffd700; font-size: 20px; font-weight: 900; line-height: 2;}
.broadcast-bar {position: fixed; top: -100px; left: 0; right: 0; background: linear-gradient(90deg, #ff0000, #aa0000); color: #fff; text-align: center; padding: 15px; font-size: 20px; font-weight: 900; z-index: 9999; transition: top 0.5s; border-bottom: 3px solid #ffd700;}
.broadcast-bar.show {top: 0;}
audio {width: 100%; margin-top: 15px;}
.lights-box {background: #111; border: 3px solid #ffd700; border-radius: 20px; padding: 15px; margin-top: 20px; overflow: hidden; width: 100%; max-width: 500px; margin: 20px auto 0;}
.rainbow-lights {display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; width: 100%;}
.light {width: 100%; aspect-ratio: 1; border-radius: 50%; animation: blink 1.5s infinite;}
@keyframes blink {0%,100%{opacity:0.3; transform:scale(0.8)} 50%{opacity:1; transform:scale(1.2)}}
@media (max-width: 600px) {.time-large {font-size: 50px}.prayer-time {font-size: 38px}.zikr-big{max-width: 100%;}}
</style>
</head>
<body>

<div class="broadcast-bar" id="broadcast-bar"></div>

<div class="container">
    <div class="logo">🌙 باب الرحمة 🌙</div>

    <div class="digital-clock">
        <div class="time-large" id="current-time">00:00:00</div>
        <div class="date-large" id="hijri-date">جاري التحميل...</div>
        <div class="date-large" id="gregorian-date"></div>
        <div class="today-day" id="today-day"></div>
    </div>

    <div class="card">
        <h2>🕌 مواقيت الصلاة</h2>
        <select id="city" onchange="loadPrayers()">
            <option value="Khartoum">الخرطوم</option>
            <option value="Omdurman">أم درمان</option>
            <option value="Makkah">مكة المكرمة</option>
        </select>
        <button class="btn" onclick="enableReminder()">🔔 تشغيل تذكير الأذان</button>
        <div id="prayers"></div>
    </div>

    <div class="card" id="zikr-card">
        <h2>📿 أذكار مصورة</h2>
        {% if adhkar %}
            {% for z in adhkar %}
                {% if z.image and z.image|length > 0 %}
                <img class="zikr-big" src="/uploads/{{z.image}}" alt="ذكر" onerror="this.style.display='none'">
                {% endif %}
            {% endfor %}
        {% else %}
        <div class="empty-zikr">لا توجد أذكار مرفوعة بعد. ارفع من لوحة الادمن</div>
        {% endif %}
    </div>

    <div class="khutba-card" id="khutba-box" style="display:none">
        <h2 style="color:#ffd700; margin-bottom:15px">📢 خطبة الجمعة</h2>
        <div style="font-size: 22px; color: #ffd700; line-height: 2.5;" id="khutba-text">خطبة الجمعة: تذكر أن الدنيا فانية والآخرة باقية</div>
    </div>

    <div class="card">
        <h2>📖 القرآن الكريم - مشاري العفاسي</h2>
        <input type="text" id="surah" placeholder="اكتب اسم السورة: البقرة، الملك، يس...">
        <button class="btn" onclick="searchQuran()">🔍 استمع</button>
        <div id="quran-result" style="margin-top:15px"></div>
    </div>

    <div class="footer">
        وقف خيري مقدم من<br>
        آل محمد بكري & آل أحمد المبارك
        <div class="lights-box">
            <div class="rainbow-lights" id="lights"></div>
        </div>
    </div>
</div>

<audio id="adhan-audio" src="https://server8.mp3quran.net/afs/001.mp3" preload="auto"></audio>

<script>
let prayerTimes = {};
let reminderEnabled = false;
const weekdays_ar = ['الأحد','الإثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'];
const surahNames = {{surah_names|tojson}};

const colors = ['#ff0000','#ff7f00','#ffff00','#00ff00','#0000ff','#4b0082','#8b00ff'];
let lightsHtml = '';
for(let i=0; i<140; i++){
    lightsHtml += `<div class="light" style="background:${colors[i%7]}; animation-delay:${i*0.05}s"></div>`;
}
document.getElementById('lights').innerHTML = lightsHtml;

setInterval(() => {
    fetch('/api/broadcast').then(r=>r.json()).then(d=>{
        if(d.text && d.time > (window.lastBroadcast || 0)) {
            window.lastBroadcast = d.time;
            const bar = document.getElementById('broadcast-bar');
            bar.innerText = '📢 ' + d.text;
            bar.classList.add('show');
            setTimeout(()=> bar.classList.remove('show'), 8000);
        }
    });
}, 3000);

function updateClock() {
    const now = new Date();
    const sudanTime = new Date(now.toLocaleString('en-US', {timeZone: 'Africa/Khartoum'}));
    const h = String(sudanTime.getHours()).padStart(2,'0');
    const m = String(sudanTime.getMinutes()).padStart(2,'0');
    const s = String(sudanTime.getSeconds()).padStart(2,'0');
    document.getElementById('current-time').innerText = `${h}:${m}:${s}`;

    const todayIndex = sudanTime.getDay();
    document.getElementById('today-day').innerText = `اليوم: ${weekdays_ar[todayIndex]}`;

    if(todayIndex === 5) { document.getElementById('khutba-box').style.display = 'block'; }
    if(h === '01' && m === '00' && s === '00'){ location.reload(); }
}
setInterval(updateClock, 1000);
updateClock();

async function loadPrayers() {
    const city = document.getElementById('city').value;
    const res = await fetch(`/api/prayers?city=${city}`);
    const data = await res.json();
    if(data.error) return;
    prayerTimes = data.timings;
    document.getElementById('hijri-date').innerText = data.hijri;
    document.getElementById('gregorian-date').innerText = data.gregorian;
    let html = '';
    for(let p in prayerTimes) {
        html += `<div class="prayer-digital"><div class="prayer-name">${p}</div><div class="prayer-time">${prayerTimes[p]}</div></div>`;
    }
    document.getElementById('prayers').innerHTML = html;
}

function enableReminder() {
    reminderEnabled = true;
    alert('🔔 تم تفعيل تذكير الأذان');
    setInterval(checkPrayerTime, 1000);
}

function checkPrayerTime() {
    if(!reminderEnabled ||!prayerTimes) return;
    const now = new Date();
    const sudanTime = new Date(now.toLocaleString('en-US', {timeZone: 'Africa/Khartoum'}));
    const current = sudanTime.getHours().toString().padStart(2,'0') + ':' + sudanTime.getMinutes().toString().padStart(2,'0');
    if(sudanTime.getSeconds() === 0) {
        for(let p in prayerTimes) {
            if(prayerTimes[p] === current) {
                document.getElementById('adhan-audio').play();
                alert(`🔔 حان وقت ${p}`);
            }
        }
    }
}

async function searchQuran() {
    const surahInput = document.getElementById('surah').value.trim();
    if(!surahInput) { alert('اكتب اسم السورة'); return; }
    let surahId = null;
    for(let id in surahNames) { if(surahNames[id] === surahInput) { surahId = id; break; } }
    if(!surahId) { alert('اسم السورة غلط. مثال: الملك، البقرة، يس'); return; }
    const res = await fetch(`/api/quran/${surahId}`);
    const data = await res.json();
    if(data.error) { alert(data.error); return; }
    document.getElementById('quran-result').innerHTML = `
        <img src="{{misari_img}}" style="width:100%; border-radius:15px; border:3px solid #ffd700; margin-bottom:10px">
        <div class="quran-text">﴿ ${data.first_ayah} ﴾</div>
        <div style="text-align:center; color:#ffd700; margin-top:10px; font-size:20px">سورة ${data.surah_name}</div>
        <audio controls autoplay src="${data.audio_url}"></audio>
    `;
}
window.onload = loadPrayers;
</script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>لوحة الأدمن</title>
<style>
body{background:#000;color:#ffd700;font-family:Cairo;padding:20px}
.box{background:#111;border:3px solid #ffd700;padding:20px;border-radius:15px;max-width:700px;margin:auto}
input,textarea{width:100%;padding:12px;margin:10px 0;background:#222;color:#ffd700;border:2px solid #ffd700;border-radius:8px;font-size:18px}
.btn{background:#ffd700;color:#000;padding:12px;border:none;border-radius:8px;font-weight:900;font-size:18px;cursor:pointer;width:100%;margin-top:10px}
.btn-del{background:#ff0000;color:#fff}
h2{text-align:center}
.zikr-item{background:#222;padding:10px;margin:10px 0;border-radius:8px;display:flex;gap:10px;align-items:center}
.zikr-item img{width:150px;height:150px;object-fit:cover;border-radius:8px;border:2px solid #ffd700}
</style></head>
<body>
<div class="box">
    <h2>🌙 لوحة تحكم باب الرحمة</h2>
    {% if not logged_in %}
    <form method="POST"><input type="password" name="password" placeholder="كلمة سر الأدمن"><button class="btn">دخول</button></form>
    {% else %}

    <h3>1. رفع أذكار مصورة فقط 📸</h3>
    <form method="POST" enctype="multipart/form-data" action="/upload">
        <input type="hidden" name="key" value="{{api_key}}">
        <input type="file" name="images" accept="image/*" multiple required>
        <small>ارفع صور الاذكار فقط. بدون كتابة</small>
        <button class="btn">رفع الصور</button>
    </form>

    <h3>2. الأذكار المرفوعة - امسح اي صورة</h3>
    {% for z in adhkar %}
    <div class="zikr-item">
        <img src="/uploads/{{z.image}}">
        <a href="/delete/{{z.id}}"><button class="btn btn-del">مسح</button></a>
    </div>
    {% else %}
    <div style="text-align:center; color:#666; padding:20px">مافي صور مرفوعة</div>
    {% endfor %}

    <h3>3. إذاعة كتابية للموقع 📢</h3>
    <form method="POST" action="/admin/broadcast">
        <textarea name="msg" rows="3" placeholder="اكتب الرسالة هنا..."></textarea>
        <button class="btn">إرسال إذاعة</button>
    </form>

    <a href="/admin/logout"><button class="btn" style="background:#ff0000;color:#fff">خروج</button></a>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def home():
    adhkar = load_adhkar()
    # فلترة: نشيل اي ذكر صورته ما موجودة
    valid_adhkar = [z for z in adhkar if z.get('image') and os.path.exists(os.path.join(UPLOAD_FOLDER, z['image']))]
    if len(valid_adhkar)!= len(adhkar):
        save_adhkar(valid_adhkar) # نصلح الملف براهو
    return render_template_string(HTML, adhkar=valid_adhkar, misari_img=MISARI_IMAGE_URL, surah_names=SURAH_NAMES)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "كلمة السر خطأ"
    return render_template_string(ADMIN_HTML, logged_in=session.get('admin'), api_key=API_KEY_UPLOAD, adhkar=load_adhkar())

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

@app.route('/admin/broadcast', methods=['POST'])
def broadcast():
    if not session.get('admin'): return "غير مصرح", 403
    global BROADCAST_MSG
    BROADCAST_MSG = {"text": request.form.get('msg'), "time": datetime.now().timestamp()}
    return redirect(url_for('admin'))

@app.route('/api/broadcast')
def get_broadcast():
    return jsonify(BROADCAST_MSG)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('key')!= API_KEY_UPLOAD or not session.get('admin'): return "غير مصرح", 403
    adhkar = load_adhkar()
    for file in request.files.getlist('images'):
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            adhkar.append({'id': uuid.uuid4().hex, 'image': filename})
    save_adhkar(adhkar)
    return redirect(url_for('admin'))

@app.route('/delete/<id>')
def delete_file(id):
    if not session.get('admin'): return "غير مصرح", 403
    adhkar = load_adhkar()
    for z in adhkar:
        if z['id'] == id:
            try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], z['image']))
            except: pass
            adhkar = [x for x in adhkar if x['id']!= id]
            break
    save_adhkar(adhkar)
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/prayers')
def get_prayers():
    city = request.args.get('city', 'Khartoum')
    try:
        res = requests.get(f'https://api.aladhan.com/v1/timingsByCity?city={city}&country=Sudan&method=2', timeout=8).json()['data']
        t, d = res['timings'], res['date']
        return jsonify({'timings': {'الفجر': t['Fajr'], 'الشروق': t['Sunrise'], 'الظهر': t['Dhuhr'], 'العصر': t['Asr'], 'المغرب': t['Maghrib'], 'العشاء': t['Isha']}, 'hijri': f"{d['hijri']['day']} {d['hijri']['month']['ar']} {d['hijri']['year']} هـ", 'gregorian': f"{d['gregorian']['day']} {d['gregorian']['month']['en']} {d['gregorian']['year']} م"})
    except:
        return jsonify({'error': 'فشل جلب المواقيت'}), 200

@app.route('/api/quran/<int:surah_id>')
def get_quran(surah_id):
    try:
        d = requests.get(f'https://api.alquran.cloud/v1/surah/{surah_id}/quran-uthmani', timeout=8).json()['data']
        return jsonify({'surah_name': d['name'], 'first_ayah': d['ayahs'][0]['text'], 'audio_url': f"https://server8.mp3quran.net/afs/{surah_id:03d}.mp3"})
    except:
        return jsonify({'error': 'رقم السورة غلط'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
