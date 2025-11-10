from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, send_file
from collections import defaultdict, Counter
import json, os, csv, io


app = Flask(__name__)

# ===== AYARLAR =====
# Adayları görsel ile tanımlıyoruz

CANDIDATES = [
    {"name": "Recep Tayyip Erdoğan", "img": "/static/img/receptayyiperdogan.jpg?v=2"},
    {"name": "Devlet Bahçeli", "img": "/static/img/devletbahceli.jpg?v=2"},
    {"name": "Selahattin Demirtaş", "img": "/static/img/selahattindemirtas.jpg?v=2"},
    {"name": "Özgür Özel", "img": "/static/img/ozgurozel.jpg?v=2"},
    {"name": "Ümit Özdağ", "img": "/static/img/umitozdag.jpg?v=2"},
    {"name": "Musavat Dervişoğlu", "img": "/static/img/musavatdervisoglu.jpg?v=2"}
]
def _check_static_images():
    base = os.path.join(os.path.dirname(__file__), "static")
    for c in CANDIDATES:
        path = c["img"].split("?")[0]
        fs = os.path.join(base, path.replace("/static/", ""))
        print(("OK   " if os.path.exists(fs) else "MISS "), fs)

WEIGHTS = [5,4,3,2,1]                 # 1.→5. sıraya puan
DATA_FILE = "data.json"               # oylar burada tutulur
ADMIN_RESET_TOKEN = "DEGIS_TIR"       # /reset?token=DEGIS_TIR
COOKIE_NAME = "tek_soru_borda_voted"  # bir tarayıcıdan 1 oy
# ====================

NAMES = [c["name"] for c in CANDIDATES]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"votes": []}  # her oy: ["Ayşe","Ali","Deniz","Ece","Can"]
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def compute_scores(votes):
    scores = defaultdict(int)
    podium_counts = {i: Counter() for i in range(5)}  # 1.lik,2.lik,... sayaçları
    for order in votes:
        for pos, name in enumerate(order):
            if pos < len(WEIGHTS):
                scores[name] += WEIGHTS[pos]
                podium_counts[pos][name] += 1
    # sıralama: toplam puan ↓, 1.lik ↓, 2.lik ↓, ... , isim ↑
    def sort_key(item):
        name, pts = item
        key = [-pts]
        for i in range(5):
            key.append(-podium_counts[i][name])
        key.append(name)
        return tuple(key)
    ranking = sorted(scores.items(), key=sort_key)
    return scores, ranking, podium_counts

@app.route("/")
def index():
    return render_template("index.html", candidates=CANDIDATES)

@app.route("/vote", methods=["POST"])
def vote():
    # 🧩 Tek oy limiti geçici olarak devre dışı bırakıldı
    # if request.cookies.get(COOKIE_NAME) == "1":
    #     return jsonify({"ok": False, "msg": "Bu tarayıcıyla zaten oy vermişsiniz."}), 429

    payload = request.get_json(force=True, silent=True) or {}
    order = payload.get("order", [])
    ok = (len(order) == len(NAMES) and set(order) == set(NAMES))
    if not ok:
        return jsonify({"ok": False, "msg": "Geçersiz sıralama."}), 400

    data = load_data()
    data["votes"].append(order)
    save_data(data)

    resp = make_response(jsonify({"ok": True}))
    # resp.set_cookie(COOKIE_NAME, "1", max_age=60*60*24*90, samesite="Lax")  # ← bu da geçici olarak kapalı
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
        podium_counts=podium,   # 🔹 tablo için GEREKLİ
    sum_weights = sum(WEIGHTS)
    )



@app.route("/export.csv")
def export_csv():
    data = load_data()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["rank1","rank2","rank3","rank4","rank5"])
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
def _check_static_images():
    import os
    base = os.path.join(os.path.dirname(__file__), "static")
    for c in CANDIDATES:
        path = c["img"].split("?")[0]  # /static/img/xxx.jpg
        fs = os.path.join(base, path.replace("/static/", ""))
        print(("OK   " if os.path.exists(fs) else "MISS "), fs)
_check_static_images()

if __name__ == "__main__":
    app.run(debug=True)






