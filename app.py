from flask import Flask, request, render_template
import requests
import os
import uuid
from datetime import datetime
from azure.cosmos import CosmosClient

app = Flask(__name__)

# ---------------- TEXT ANALYTICS ----------------
endpoint = os.environ.get("AZURE_ENDPOINT")
key = os.environ.get("AZURE_KEY")

# ---------------- COSMOS DB ----------------
container = None

try:
    cosmos_uri = os.environ.get("COSMOS_URI")
    cosmos_key = os.environ.get("COSMOS_KEY")
    database_name = os.environ.get("COSMOS_DB")
    container_name = os.environ.get("COSMOS_CONTAINER")

    if all([cosmos_uri, cosmos_key, database_name, container_name]):
        client = CosmosClient(cosmos_uri, cosmos_key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        print("✅ Cosmos DB connected")

except Exception as e:
    print("❌ Cosmos DB connection failed:", str(e))
    container = None   # VERY IMPORTANT


# ---------------- ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def index():

    sentiment = None

    if request.method == "POST":

        text = request.form.get("text")

        try:
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

        except Exception as e:
            sentiment = "API Error"
            print("Text Analytics Error:", e)

        # -------- SAVE TO COSMOS SAFELY --------
        if container and sentiment:
            try:
                item = {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "sentiment": sentiment,
                    "timestamp": str(datetime.utcnow())
                }

                container.create_item(body=item)

            except Exception as e:
                print("Cosmos insert failed:", e)

    return render_template("index.html", sentiment=sentiment)


# ---------------- AZURE ENTRY ----------------
if __name__ == "__main__":
    app.run()
