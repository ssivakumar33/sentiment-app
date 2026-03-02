from flask import Flask, request, render_template
import requests
import os

app = Flask(__name__)

endpoint = os.environ.get("AZURE_ENDPOINT")
key = os.environ.get("AZURE_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None

    if request.method == "POST":
        text = request.form["text"]

        # SAFE CHECK
        if not endpoint or not key:
            sentiment = "Azure environment variables missing"
        else:
            url = endpoint + "/text/analytics/v3.1/sentiment"

            headers = {
                "Ocp-Apim-Subscription-Key": key,
                "Content-Type": "application/json"
            }

            body = {
                "documents": [
                    {"id": "1", "language": "en", "text": text}
                ]
            }

            response = requests.post(url, headers=headers, json=body)
            result = response.json()

            sentiment = result["documents"][0]["sentiment"]

    return render_template("index.html", sentiment=sentiment)
