import os
import json
from datetime import date
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
USAGE_FILE = BASE_DIR / "usage.json"

QUOTA = {
    "chat": 5,
    "image": 10,
    "video": 5
}

def today_key():
    return date.today().isoformat()

def load_usage():
    if not USAGE_FILE.exists():
        return {}
    try:
        return json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_usage(data):
    USAGE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_today_usage():
    data = load_usage()
    today = today_key()
    if today not in data:
        data[today] = {"chat": 0, "image": 0, "video": 0}
        save_usage(data)
    return data[today]

def can_use(kind):
    usage = get_today_usage()
    return usage.get(kind, 0) < QUOTA.get(kind, 0)

def consume(kind):
    data = load_usage()
    today = today_key()
    if today not in data:
        data[today] = {"chat": 0, "image": 0, "video": 0}
    data[today][kind] = data[today].get(kind, 0) + 1
    save_usage(data)

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY غير موجود. اكتب المفتاح داخل ملف .env")
    return OpenAI(api_key=api_key)

def generate_chat_response(prompt):
    client = get_client()
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text

def generate_image_response(prompt):
    client = get_client()

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        url = response.data[0].url
        return {
            "status": "success",
            "url": url
        }
    except Exception as e:
        return {
            "status": "fallback",
            "message": f"Image generation failed: {str(e)}",
            "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
        }

def generate_video_response(prompt):
    # OpenAI image/video generation APIs differ by service.
    # This demo mode works without extra provider setup.
    return {
        "status": "demo",
        "message": "ميزة الفيديو تعمل كـ demo محلي لأنك تحتاج provider خارجي مثل Replicate/Fal لحل الفيديو الحقيقي.",
        "prompt": prompt,
        "url": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/usage")
def usage():
    return jsonify({
        "quota": QUOTA,
        "used": get_today_usage()
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()

    if not prompt:
        return jsonify({"error": "أدخل نصًا أوليًا"}), 400

    if not can_use("chat"):
        return jsonify({
            "error": "لقد وصلت إلى حد المحادثات اليومي.",
            "quota": QUOTA,
            "used": get_today_usage()
        }), 429

    consume("chat")
    try:
        answer = generate_chat_response(prompt)
        return jsonify({
            "answer": answer,
            "quota": QUOTA,
            "used": get_today_usage()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/image", methods=["POST"])
def api_image():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()

    if not prompt:
        return jsonify({"error": "أدخل وصف الصورة أولًا"}), 400

    if not can_use("image"):
        return jsonify({
            "error": "لقد وصلت إلى حد الصور اليومي.",
            "quota": QUOTA,
            "used": get_today_usage()
        }), 429

    consume("image")
    result = generate_image_response(prompt)
    return jsonify({
        "result": result,
        "quota": QUOTA,
        "used": get_today_usage()
    })

@app.route("/api/video", methods=["POST"])
def api_video():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()

    if not prompt:
        return jsonify({"error": "أدخل وصف الفيديو أولًا"}), 400

    if not can_use("video"):
        return jsonify({
            "error": "لقد وصلت إلى حد الفيديوهات اليومي.",
            "quota": QUOTA,
            "used": get_today_usage()
        }), 429

    consume("video")
    result = generate_video_response(prompt)
    return jsonify({
        "result": result,
        "quota": QUOTA,
        "used": get_today_usage()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
