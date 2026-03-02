from flask import Flask, request, render_template
import requests
import os
from azure.cosmos import CosmosClient
import uuid
from datetime import datetime

app = Flask(__name__)

# ---------- Text Analytics ----------
endpoint = os.environ.get("AZURE_ENDPOINT")
key = os.environ.get("AZURE_KEY")

# ---------- Cosmos DB ----------
cosmos_uri = os.environ.get("COSMOS_URI")
cosmos_key = os.environ.get("COSMOS_KEY")
database_name = os.environ.get("COSMOS_DB")
container_name = os.environ.get("COSMOS_CONTAINER")

client = CosmosClient(cosmos_uri, cosmos_key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)


@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None

    if request.method == "POST":
        text = request.form["text"]

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

        # ---------- SAVE TO COSMOS DB ----------
        item = {
            "id": str(uuid.uuid4()),
            "text": text,
            "sentiment": sentiment,
            "timestamp": str(datetime.utcnow())
        }

        container.create_item(body=item)

    return render_template("index.html", sentiment=sentiment)


if __name__ == "__main__":
    app.run()
