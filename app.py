import os
import json
from datetime import datetime, date
from pathlib import Path

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

BASE_DIR = Path(__file__).resolve().parent
USAGE_PATH = BASE_DIR / "usage.json"

QUOTA = {
    "chat": 5,
    "image": 10,
    "video": 5
}

def today_key():
    return date.today().isoformat()

def load_usage():
    if not USAGE_PATH.exists():
        return {}
    try:
        return json.loads(USAGE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_usage(data):
    USAGE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_user_usage():
    data = load_usage()
    today = today_key()
    if today not in data:
        data[today] = {"chat": 0, "image": 0, "video": 0}
        save_usage(data)
    return data[today]

def can_use(kind):
    usage = get_user_usage()
    return usage.get(kind, 0) < QUOTA.get(kind, 0)

def consume(kind):
    data = load_usage()
    today = today_key()
    if today not in data:
        data[today] = {"chat": 0, "image": 0, "video": 0}
    data[today][kind] = data[today].get(kind, 0) + 1
    save_usage(data)

def mock_text(prompt):
    return (
        f"هذا رد تجريبي من AMIRXTNA.\n"
        f"السؤال: {prompt}\n\n"
        "الذكاء الاصطناعي الحقيقي يحتاج API key. "
        "أضف OpenAI أو خدمة أخرى وتفعّلها في المشروع."
    )

def mock_image(prompt):
    return {
        "status": "demo",
        "message": "هذا مثال تجريبي لانتاج صورة",
        "prompt": prompt,
        "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
    }

def mock_video(prompt):
    return {
        "status": "demo",
        "message": "هذا مثال تجريبي لانتاج فيديو",
        "prompt": prompt,
        "url": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
    }

def generate_real_text(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return mock_text(prompt)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"حدث خطأ في OpenAI: {str(e)}"

def generate_real_image(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return mock_image(prompt)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        return {
            "status": "success",
            "url": response.data[0].url
        }
    except Exception as e:
        return {
            "status": "fallback",
            "message": f"API image failed: {str(e)}",
            "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/usage")
def usage():
    return jsonify({
        "quota": QUOTA,
        "used": get_user_usage()
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify({"error": "أدخل نصًا أولًا"}), 400

    if not can_use("chat"):
        return jsonify({
            "error": "لقد وصلت إلى حد المحادثات اليومي.",
            "quota": QUOTA,
            "used": get_user_usage()
        }), 429

    consume("chat")
    answer = generate_real_text(prompt)
    return jsonify({
        "answer": answer,
        "quota": QUOTA,
        "used": get_user_usage()
    })

@app.route("/api/image", methods=["POST"])
def image():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify({"error": "أدخل وصف الصورة أولًا"}), 400

    if not can_use("image"):
        return jsonify({
            "error": "لقد وصلت إلى حد الصور اليومي.",
            "quota": QUOTA,
            "used": get_user_usage()
        }), 429

    consume("image")
    result = generate_real_image(prompt)
    return jsonify({
        "result": result,
        "quota": QUOTA,
        "used": get_user_usage()
    })

@app.route("/api/video", methods=["POST"])
def video():
    data = request.get_json(force=True, silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify({"error": "أدخل وصف الفيديو أولًا"}), 400

    if not can_use("video"):
        return jsonify({
            "error": "لقد وصلت إلى حد الفيديوهات اليومي.",
            "quota": QUOTA,
            "used": get_user_usage()
        }), 429

    consume("video")
    # Video generation requires separate API like Replicate/Fal.ai
    result = mock_video(prompt)
    return jsonify({
        "result": result,
        "quota": QUOTA,
        "used": get_user_usage()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
