from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["events"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event")

    data = {"timestamp": datetime.utcnow()}

    if event_type == "push":
        data.update({
            "type": "push",
            "author": payload["pusher"]["name"],
            "to_branch": payload["ref"].split("/")[-1]
        })

    elif event_type == "pull_request":
        data.update({
            "type": "pull_request",
            "author": payload["pull_request"]["user"]["login"],
            "from_branch": payload["pull_request"]["head"]["ref"],
            "to_branch": payload["pull_request"]["base"]["ref"]
        })

    elif event_type == "merge":
        data.update({
            "type": "merge",
            "author": payload["sender"]["login"],
            "from_branch": payload["pull_request"]["head"]["ref"],
            "to_branch": payload["pull_request"]["base"]["ref"]
        })

    collection.insert_one(data)
    return jsonify({"status": "received"}), 200

@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)

if __name__ == "__main__":
    app.run(port=5000)
