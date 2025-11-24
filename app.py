from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, send_file
import json, os, io, csv
from collections import defaultdict, Counter
import uuid as _uuid

# ===== APP =====
app = Flask(__name__)

# ===== UUID CACHE KIRICI =====
def uuid():
    return _uuid.uuid4()
app.jinja_env.globals['uuid'] = uuid


# ===== AYARLAR =====
CANDIDATES = [
    {"name": "Recep Tayyip Erdoğan",   "img": "/static/img/receptayyiperdogan.jpg?v=2"},
    {"name": "Devlet Bahçeli",         "img": "/static/img/devletbahceli.jpg?v=2"},
    {"name": "Selahattin Demirtaş",    "img": "/static/img/selahattindemirtas.jpg?v=2"},
    {"name": "Özgür Özel",             "img": "/static/img/ozgurozel.jpg?v=2"},
    {"name": "Ümit Özdağ",             "img": "/static/img/umitozdag.jpg?v=2"},
    {"name": "Musavat Dervişoğlu",     "img": "/static/img/musavatdervisoglu.jpg?v=2"}
]

WEIGHTS = [6,5, 4, 3, 2, 1]
DATA_FILE = "data.json"
ADMIN_RESET_TOKEN = "DEGIS_TIR"
COOKIE_NAME = "tek_soru_borda_voted"

NAMES = [c["name"] for c in CANDIDATES]

# ===== DATA =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"votes": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== BORDA HESAPLAMA =====
# ===== BORDA HESAPLAMA =====
def compute_scores(votes):
    scores = defaultdict(int)
    podium_counts = {i: Counter() for i in range(len(NAMES))}

    for order in votes:
        for pos, name in enumerate(order):
            if pos < len(WEIGHTS):
                scores[name] += WEIGHTS[pos]
                podium_counts[pos][name] += 1

    def sort_key(item):
        name, pts = item
        key = [-pts]
        for i in range(len(NAMES)):
            key.append(-podium_counts[i][name])
        key.append(name)
        return tuple(key)

    ranking = sorted(scores.items(), key=sort_key)
    return scores, ranking, podium_counts

# ===== CACHE KIRICI =====
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ===== ROUTES =====
@app.route("/")
def index():
    return render_template("index.html", candidates=CANDIDATES)

@app.route("/vote", methods=["POST"])
def vote():
    payload = request.get_json(force=True, silent=True) or {}
    order = payload.get("order", [])
    ok = (len(order) == len(NAMES) and set(order) == set(NAMES))

    if not ok:
        return jsonify({"ok": False, "msg": "Geçersiz sıralama."}), 400

    data = load_data()
    data["votes"].append(order)
    save_data(data)

    resp = make_response(jsonify({"ok": True}))
    return resp

@app.route("/results")
def results():
    data = load_data()
    scores, ranking, podium = compute_scores(data["votes"])
    winner = ranking[0][0] if ranking else None
    total_votes = len(data["votes"])
    imgs = {c["name"]: c["img"] for c in CANDIDATES}

    return render_template(
        "results.html",
        candidates=CANDIDATES,
        scores=dict(scores),
        ranking=ranking,
        winner=winner,
        total_votes=total_votes,
        imgs=imgs,
        podium_counts=podium,
        sum_weights=sum(WEIGHTS)
    )

@app.route("/export.csv")
def export_csv():
    data = load_data()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["rank1","rank2","rank3","rank4","rank5","rank6"])
    for order in data["votes"]:
        w.writerow(order)
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="votes_export.csv")

@app.route("/reset")
def reset():
    token = request.args.get("token", "")
    if token != ADMIN_RESET_TOKEN:
        return "Yetkisiz.", 403
    save_data({"votes": []})
    resp = make_response(redirect(url_for("results")))
    resp.delete_cookie(COOKIE_NAME)
    return resp


# ===== GÖRSELLERİ KONTROL =====
def _check_static_images():
    base = os.path.join(os.path.dirname(__file__), "static")
    for c in CANDIDATES:
        path = c["img"].split("?")[0]
        fs = os.path.join(base, path.replace("/static/", ""))
        print(("OK   " if os.path.exists(fs) else "MISS "), fs)
_check_static_images()
# ==== STEALTH GOOGLE BOT PING ====
import threading, time, requests

def _keep_awake():
    url = "https://tek-soru-borda-images.onrender.com/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        )
    }
    while True:
        try:
            requests.get(url, headers=headers, timeout=5)
        except:
            pass
        time.sleep(240)  # 4 dakika

threading.Thread(target=_keep_awake, daemon=True).start()
# ==== STEALTH GOOGLE BOT PING ====
import threading, time, requests

def _keep_awake():
    url = "https://tek-soru-borda-images.onrender.com/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        )
    }
    while True:
        try:
            requests.get(url, headers=headers, timeout=5)
        except:
            pass
        time.sleep(240)  # 4 dakika

threading.Thread(target=_keep_awake, daemon=True).start()

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
