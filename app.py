from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"])
db = client[app.config["DB_NAME"]]
listings_collection = db["listings"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-listing", methods=["GET", "POST"])
def create_listing():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        user_type = request.form.get("user_type")
        location = request.form.get("location")
        contact = request.form.get("contact")

        listing = {
            "title": title,
            "description": description,
            "user_type": user_type,
            "location": location,
            "contact": contact,
            "created_at": datetime.utcnow()
        }

        listings_collection.insert_one(listing)

        return redirect(url_for("home"))

    return render_template("create_listing.html")


if __name__ == "__main__":
    app.run(debug=True)