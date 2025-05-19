from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "relevant123"

DATA_FILE = "data.json"
BACKGROUND_FILE = "background.txt"
ADMIN_PASSWORD = "relevant123"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_background():
    if os.path.exists(BACKGROUND_FILE):
        with open(BACKGROUND_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_background(url):
    with open(BACKGROUND_FILE, "w") as f:
        f.write(url)

@app.route("/")
def index():
    offers = load_data()
    background = load_background()
    return render_template("index.html", offers=offers, background=background)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "logged_in" not in session:
        if request.method == "POST":
            if request.form.get("password") == ADMIN_PASSWORD:
                session["logged_in"] = True
                return redirect(url_for("admin"))
        return render_template("login.html")

    offers = load_data()
    background = load_background()
    return render_template("admin.html", offers=offers, background=background)

@app.route("/add", methods=["POST"])
def add():
    if "logged_in" in session:
        offers = load_data()
        new_offer = {
            "title": request.form.get("title"),
            "subtitle": request.form.get("subtitle"),
            "image": request.form.get("image"),
            "url": request.form.get("url"),
            "button": request.form.get("button")
        }
        offers.append(new_offer)
        save_data(offers)
    return redirect(url_for("admin"))

@app.route("/delete/<int:index>")
def delete(index):
    if "logged_in" in session:
        offers = load_data()
        if 0 <= index < len(offers):
            offers.pop(index)
            save_data(offers)
    return redirect(url_for("admin"))

@app.route("/set_background", methods=["POST"])
def set_background():
    if "logged_in" in session:
        bg_url = request.form.get("background")
        save_background(bg_url)
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
