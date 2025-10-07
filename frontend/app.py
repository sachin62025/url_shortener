import os
from flask import Flask, request, render_template
import requests
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    short_url = None
    if request.method == "POST":
        long_url = request.form.get("url")
        try:
            r = requests.post(f"{BACKEND_URL}/api/create", json={"url": long_url}, timeout=5)
            r.raise_for_status()
            short_url = r.json().get("short_url")
        except Exception as e:
            error = str(e)
    return render_template("index.html", short_url=short_url, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
