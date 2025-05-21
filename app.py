
from flask import Flask, render_template, request, redirect, session, send_file
import json, os

app = Flask(__name__)
app.secret_key = "relevant123"

DATA_FILE = "data.json"
BG_FILE = "background.txt"
HEADER_FILE = "header.txt"

def load_data():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else []

@app.route("/")
def index():
    offers = load_data()
    bg = open(BG_FILE).read() if os.path.exists(BG_FILE) else ""
    header_text = open(HEADER_FILE).read() if os.path.exists(HEADER_FILE) else ""
    return render_template("index.html", offers=offers, background=bg, header_text=header_text)

@app.route("/admin", methods=["GET"])
def admin():
    if not session.get("auth"):
        return redirect("/login")
    offers = load_data()
    bg = open(BG_FILE).read() if os.path.exists(BG_FILE) else ""
    header_text = open(HEADER_FILE).read() if os.path.exists(HEADER_FILE) else ""
    return render_template("admin.html", offers=offers, background=bg, header_text=header_text, edit_offer=None, edit_index=None)

@app.route("/edit/<int:idx>", methods=["GET", "POST"])
def edit_offer(idx):
    if not session.get("auth"):
        return redirect("/login")
    offers = load_data()
    if request.method == "POST":
        offers[idx] = {
            "title": request.form["title"],
            "subtitle": request.form["subtitle"],
            "image": request.form["image"],
            "url": request.form["url"],
            "button": request.form["button"],
            "timer": int(request.form["timer"]),
        }
        json.dump(offers, open(DATA_FILE, "w"), indent=2)
        return redirect("/admin")
    else:
        offer = offers[idx]
        return render_template("admin.html", offers=offers, edit_offer=offer, edit_index=idx,
                               background=open(BG_FILE).read() if os.path.exists(BG_FILE) else "",
                               header_text=open(HEADER_FILE).read() if os.path.exists(HEADER_FILE) else "")

@app.route("/set_header", methods=["POST"])
def set_header():
    if not session.get("auth"):
        return redirect("/login")
    with open(HEADER_FILE, "w") as f:
        f.write(request.form.get("header", ""))
    return redirect("/admin")

@app.route("/add", methods=["POST"])
def add():
    if not session.get("auth"):
        return redirect("/login")
    offers = load_data()
    offers.append({
        "title": request.form["title"],
        "subtitle": request.form["subtitle"],
        "image": request.form["image"],
        "url": request.form["url"],
        "button": request.form["button"],
        "timer": int(request.form["timer"]),
    })
    json.dump(offers, open(DATA_FILE, "w"), indent=2)
    return redirect("/admin")

@app.route("/delete/<int:idx>")
def delete(idx):
    if not session.get("auth"):
        return redirect("/login")
    offers = load_data()
    if 0 <= idx < len(offers):
        offers.pop(idx)
    json.dump(offers, open(DATA_FILE, "w"), indent=2)
    return redirect("/admin")

@app.route("/export")
def export():
    if not session.get("auth"):
        return redirect("/login")
    return send_file(DATA_FILE, as_attachment=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("password") == "relevant123":
        session["auth"] = True
        return redirect("/admin")
    return "<form method='post'><input name='password' type='password'><button>Login</button></form>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/track", methods=["POST"])
def track():
    from flask import jsonify
    data = request.get_json()
    idx = int(data.get("index", -1))
    action = data.get("action")
    offers = load_data()
    if 0 <= idx < len(offers) and action in ("clicks", "views"):
        offers[idx][action] = offers[idx].get(action, 0) + 1
        json.dump(offers, open(DATA_FILE, "w"), indent=2)
        return jsonify(success=True)
    return jsonify(success=False), 400

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
