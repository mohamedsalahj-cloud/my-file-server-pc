from flask import Flask, request, render_template_string, send_from_directory, redirect, session
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "pi_tunisia_it_engineer_key"
PASSWORD = "0000"

BASE_DIR = "/app/uploads"
DIRS = {
    "postformat": os.path.join(BASE_DIR, "postformat"),
    "office": os.path.join(BASE_DIR, "office"),
    "win7": os.path.join(BASE_DIR, "win7"),
    "win8": os.path.join(BASE_DIR, "win8"),
    "win10": os.path.join(BASE_DIR, "win10"),
    "win11": os.path.join(BASE_DIR, "win11"),
    "linux": os.path.join(BASE_DIR, "linux"),
    "media": os.path.join(BASE_DIR, "media")
}
META_FILE = os.path.join(BASE_DIR, "meta.json")

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

for item in os.listdir(BASE_DIR):
    p = os.path.join(BASE_DIR, item)
    if os.path.isfile(p) and item != "meta.json":
        os.rename(p, os.path.join(DIRS["media"], item))

def load_meta():
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_meta(data):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fmt_size(path):
    try:
        b = os.path.getsize(path)
        for u in ["B", "KB", "MB", "GB"]:
            if b < 1024: return f"{b:.1f} {u}"
            b /= 1024
    except Exception:
        pass
    return ""

SIDE_GLOW = """
<style>
  @keyframes pulseOrb { 0%,100%{transform:translateY(-50%) scale(1);box-shadow:0 0 25px rgba(251,180,74,0.45);} 50%{transform:translateY(-50%) scale(1.08);box-shadow:0 0 55px rgba(251,180,74,0.9),0 0 85px rgba(168,85,247,0.6);} }
  .grid-bg { background-color: #12071f; background-image: radial-gradient(rgba(251,180,74,0.12) 1px, transparent 1px), radial-gradient(circle at top, #2e104d, #0f051a); background-size: 28px 28px, 100% 100%; }
  .pi-orb { position:fixed; top:50%; width:74px; height:74px; border-radius:50%; background:radial-gradient(circle at 30% 30%, #fde047, #b45309); border:3px solid #fef3c7; color:#1e0836; font-size:38px; font-weight:bold; display:flex; align-items:center; justify-content:center; animation:pulseOrb 3.5s infinite ease-in-out; pointer-events:none; z-index:2; }
  .orb-r { right:1.8%; } .orb-l { left:1.8%; }
  @media (max-width:1380px) { .pi-orb { display:none; } }
</style>
<div class="pi-orb orb-r">π</div>
<div class="pi-orb orb-l">π</div>
"""

TN_FLAG = """<svg width="32" height="22" viewBox="0 0 36 24" style="border-radius:4px;box-shadow:0 0 8px rgba(231,0,19,0.6);vertical-align:middle;"><rect width="36" height="24" fill="#E70013"/><circle cx="18" cy="12" r="6" fill="#FFFFFF"/><circle cx="19.2" cy="12" r="4.6" fill="#E70013"/><polygon points="20.5,12 17.8,12.9 19.5,10.6 19.5,13.4 17.8,11.1" fill="#FFFFFF"/></svg>"""

LOGIN_HTML = """<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>بوابة مهندس الإعلامية</title><style>body{font-family:Tahoma,Arial;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}.card{background:rgba(28,11,48,0.94);border:1px solid rgba(251,180,74,0.5);padding:40px 30px;border-radius:24px;text-align:center;width:90%;max-width:390px;}.logo{width:76px;height:76px;margin:0 auto 15px;border-radius:50%;background:linear-gradient(135deg,#fbb44a,#d97706);color:#1e0836;font-size:42px;font-weight:bold;display:flex;align-items:center;justify-content:center;}h2{color:#fbb44a;margin:5px 0;}p{color:#d8b4fe;font-size:13px;}input{width:85%;padding:14px;margin:15px 0;border-radius:12px;border:1px solid #9333ea;background:#11061e;color:#fbb44a;text-align:center;font-size:18px;letter-spacing:4px;}.btn{background:linear-gradient(135deg,#fbb44a,#f59e0b);color:#1e0836;border:none;padding:14px;border-radius:12px;cursor:pointer;font-weight:bold;font-size:16px;width:92%;}</style></head><body class="grid-bg">""" + SIDE_GLOW + """<div class="card"><div class="logo">π</div><h2>محطة المهندس السحابية """ + TN_FLAG + """</h2><p>IT Engineer Cloud • Tunisia</p><form method="post"><input type="password" name="password" placeholder="••••••" required><br><button class="btn" type="submit">🔓 دخول النظام</button></form>{% if err %}<p style="color:#f87171;">{{ err }}</p>{% endif %}</div></body></html>"""
MAIN_HTML = """<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>IT Engineer Pi Cloud</title><style>
  body { font-family:Tahoma,Arial,sans-serif; color:#f8fafc; margin:0; padding:22px 15px; min-height:100vh; }
  .container { position:relative; z-index:10; max-width:1240px; margin:auto; }
  .topbar { display:flex; justify-content:space-between; align-items:center; background:rgba(30,12,50,0.92); border:1px solid rgba(251,180,74,0.45); padding:16px 24px; border-radius:20px; margin-bottom:22px; }
  .brand { display:flex; align-items:center; gap:14px; }
  .badge { width:48px; height:48px; border-radius:50%; background:linear-gradient(135deg,#fbb44a,#d97706); color:#1e0836; font-size:26px; font-weight:bold; display:flex; align-items:center; justify-content:center; }
  .brand h1 { color:#fbb44a; margin:0; font-size:19px; display:flex; align-items:center; gap:10px; }
  .brand span { color:#c084fc; font-size:12px; }
  .logout { background:rgba(239,68,68,0.2); border:1px solid #ef4444; color:#fca5a5; text-decoration:none; padding:8px 15px; border-radius:10px; font-size:13px; font-weight:bold; }
  .grid-os { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; }
  @media (max-width:1150px) { .grid-os { grid-template-columns:repeat(2, 1fr); } }
  @media (max-width:650px) { .grid-os { grid-template-columns:1fr; } }
  .panel { background:rgba(30,12,50,0.92); border:1px solid rgba(168,85,247,0.35); border-radius:18px; padding:16px; }
  .p-pf { border-top:4px solid #f43f5e; } .p-pf h2 { color:#fb7185; }
  .p-off { border-top:4px solid #10b981; } .p-off h2 { color:#34d399; }
  .p-w7 { border-top:4px solid #60a5fa; } .p-w7 h2 { color:#60a5fa; }
  .p-w8 { border-top:4px solid #22d3ee; } .p-w8 h2 { color:#22d3ee; }
  .p-w10 { border-top:4px solid #38bdf8; } .p-w10 h2 { color:#38bdf8; }
  .p-w11 { border-top:4px solid #818cf8; } .p-w11 h2 { color:#818cf8; }
  .p-lin { border-top:4px solid #fbb44a; } .p-lin h2 { color:#fbb44a; }
  .p-med { border-top:4px solid #e879f9; } .p-med h2 { color:#e879f9; }
  .panel h2 { margin-top:0; font-size:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:9px; }
  .upload-box { background:rgba(15,6,26,0.8); border:1px dashed rgba(255,255,255,0.25); padding:11px; border-radius:12px; margin-bottom:12px; text-align:center; }
  .txt-in { width:92%; padding:7px; margin-bottom:8px; border-radius:7px; border:1px solid #6b21a8; background:#19092b; color:#fff; font-size:11px; }
  input[type=file] { color:#e9d5ff; margin-bottom:8px; font-size:11px; width:92%; }
  .btn { border:none; padding:8px 14px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:12px; width:96%; color:#fff; }
  .b-pf { background:#e11d48; } .b-off { background:#059669; } .b-w7 { background:#2563eb; } .b-w8 { background:#0891b2; } .b-w10 { background:#0284c7; } .b-w11 { background:#4f46e5; }
  .b-lin { background:linear-gradient(135deg,#d97706,#fbb44a); color:#1e0836; } .b-med { background:linear-gradient(135deg,#a21caf,#d946ef); }
  .item { background:rgba(52,22,82,0.65); border:1px solid rgba(168,85,247,0.25); padding:8px 10px; border-radius:9px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; gap:6px; }
  .info { overflow:hidden; }
  .fname { font-weight:bold; font-size:11px; color:#fef3c7; word-break:break-all; display:block; }
  .fnote { font-size:10px; color:#d8b4fe; margin-top:2px; display:block; }
  .fsize { font-size:9px; color:#94a3b8; background:rgba(0,0,0,0.35); padding:1px 5px; border-radius:4px; display:inline-block; margin-top:2px; }
  .btns { display:flex; gap:4px; flex-shrink:0; }
  .btns a { text-decoration:none; padding:4px 8px; border-radius:5px; font-size:10px; font-weight:bold; color:#fff; }
  .dl { background:#6d28d9; } .del { background:#dc2626; }
</style></head><body class="grid-bg">""" + SIDE_GLOW + """
<div class="container">
  <div class="topbar">
    <div class="brand"><div class="badge">π</div><div><h1>سحابة مهندس الإعلامية • Pi Cloud """ + TN_FLAG + """</h1><span>برامج ما بعد الفورمات • الأوفيس • Windows 7/8/10/11 • Linux • الأفلام</span></div></div>
    <a class="logout" href="/logout">🔒 قفل المحطة</a>
  </div>
  <div class="grid-os">
    {% set sections = [
      ('postformat', 'p-pf', 'b-pf', '🧰 برامج ما بعد الفورمات', '🔧', 'تحميل', 'download'),
      ('office', 'p-off', 'b-off', '📊 برامج الأوفيس Office', '📑', 'تحميل', 'download'),
      ('win7', 'p-w7', 'b-w7', '🪟 برامج Windows 7', '💠', 'تحميل', 'download'),
      ('win8', 'p-w8', 'b-w8', '🪟 برامج Windows 8', '💠', 'تحميل', 'download'),
      ('win10', 'p-w10', 'b-w10', '🪟 برامج Windows 10', '💠', 'تحميل', 'download'),
      ('win11', 'p-w11', 'b-w11', '🪟 برامج Windows 11', '💠', 'تحميل', 'download'),
      ('linux', 'p-lin', 'b-lin', '🐧 أدوات Linux & Scripts', '⚙️', 'تحميل', 'download'),
      ('media', 'p-med', 'b-med', '🎬 الأفلام والفيديوهات', '🎬', 'مشاهدة', 'view')
    ] %}
    {% for key, pcls, bcls, title, icon, act_txt, act_url in sections %}
    <div class="panel {{ pcls }}">
      <h2>{{ title }} ({{ data[key]|length }})</h2>
      <form class="upload-box" action="/upload/{{ key }}" method="post" enctype="multipart/form-data">
        <input class="txt-in" type="text" name="note" placeholder="اسم البرنامج أو ملاحظة">
        <input type="file" name="files" multiple required>
        <button class="btn {{ bcls }}" type="submit">⬆️ رفع الملفات</button>
      </form>
      {% for f in data[key] %}
      <div class="item">
        <div class="info"><span class="fname">{{ icon }} {{ f.name }}</span>{% if f.note %}<span class="fnote">📌 {{ f.note }}</span>{% endif %}<span class="fsize">{{ f.size }}</span></div>
        <div class="btns"><a class="dl" href="/{{ act_url }}/{{ key }}/{{ f.name }}" {% if act_url=='view' %}target="_blank"{% endif %}>{{ act_txt }}</a><a class="del" href="/delete/{{ key }}/{{ f.name }}">حذف</a></div>
      </div>
      {% else %}<p style="text-align:center;color:#94a3b8;font-size:11px;">فارغ</p>{% endfor %}
    </div>
    {% endfor %}
  </div>
</div>
</body></html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        err = "الرقم السري غير صحيح!"
    return render_template_string(LOGIN_HTML, err=err)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if not session.get("logged_in"): return redirect("/login")
    meta = load_meta()
    data = {cat: [{"name": n, "note": meta.get(f"{cat}/{n}", ""), "size": fmt_size(os.path.join(folder, n))} for n in sorted(os.listdir(folder))] for cat, folder in DIRS.items()}
    return render_template_string(MAIN_HTML, data=data)

@app.route("/upload/<category>", methods=["POST"])
def upload(category):
    if not session.get("logged_in") or category not in DIRS: return redirect("/login")
    note = request.form.get("note", "").strip()
    meta = load_meta()
    for f in request.files.getlist("files"):
        if f and f.filename:
            name = secure_filename(f.filename) or f.filename
            f.save(os.path.join(DIRS[category], name))
            if note: meta[f"{category}/{name}"] = note
    save_meta(meta)
    return redirect("/")

@app.route("/download/<category>/<path:filename>")
def download(category, filename):
    return send_from_directory(DIRS[category], filename, as_attachment=True) if session.get("logged_in") and category in DIRS else redirect("/login")

@app.route("/view/<category>/<path:filename>")
def view(category, filename):
    return send_from_directory(DIRS[category], filename) if session.get("logged_in") and category in DIRS else redirect("/login")

@app.route("/delete/<category>/<path:filename>")
def delete(category, filename):
    if not session.get("logged_in") or category not in DIRS: return redirect("/login")
    p = os.path.join(DIRS[category], filename)
    if os.path.exists(p): os.remove(p)
    meta = load_meta(); meta.pop(f"{category}/{filename}", None); save_meta(meta)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
