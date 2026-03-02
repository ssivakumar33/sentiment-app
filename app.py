from flask import Flask, request, render_template
import requests
import os
import uuid
from azure.cosmos import CosmosClient

app = Flask(__name__)

# ==============================
# Azure Text Analytics Settings
# ==============================
endpoint = os.environ.get("AZURE_ENDPOINT")
key = os.environ.get("AZURE_KEY")

# ==============================
# Cosmos DB Connection
# ==============================
cosmos_uri = os.environ.get("COSMOS_URI")
cosmos_key = os.environ.get("COSMOS_KEY")

client = CosmosClient(cosmos_uri, credential=cosmos_key)
database = client.get_database_client("sentimentdb")
container = database.get_container_client("sentiments")


# ==============================
# Main Route
# ==============================
@app.route("/", methods=["GET", "POST"])
def index():

    sentiment = None

    if request.method == "POST":

        text = request.form["text"]

        # Azure Sentiment API
        url = endpoint + "/text/analytics/v3.1/sentiment"

        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/json"
        }

        body = {
            "documents": [
                {
                    "id": "1",
                    "language": "en",
                    "text": text
                }
            ]
        }

        response = requests.post(url, headers=headers, json=body)
        result = response.json()

        sentiment = result["documents"][0]["sentiment"]

        # ==============================
        # Store Result in Cosmos DB
        # ==============================
        container.create_item({
            "id": str(uuid.uuid4()),
            "text": text,
            "sentiment": sentiment
        })

    return render_template("index.html", sentiment=sentiment)


# Azure App Service uses Gunicorn
if __name__ == "__main__":
    app.run()
