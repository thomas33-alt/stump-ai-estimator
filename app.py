from flask import Flask, request, jsonify
import base64
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PRICE_PER_INCH = 4.5
MINIMUM = 85

@app.route("/", methods=["GET"])
def home():
    return "Stump AI Estimator Running"

@app.route("/estimate", methods=["POST"])
def estimate():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    image_bytes = file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Estimate the diameter in inches of the tree stump in this image. Assume the photo was taken from 3-6 feet away. Respond with only a number."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    diameter = float(response.choices[0].message.content.strip())

    base_price = max(diameter * PRICE_PER_INCH, MINIMUM)
    low = base_price * 0.85
    high = base_price * 1.15

    return jsonify({
        "diameter_inches": round(diameter, 1),
        "price_low": round(low, 2),
        "price_high": round(high, 2)
    })

if __name__ == "__main__":
    app.run()
