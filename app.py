from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from config import Config
from datetime import datetime, UTC
from bson.objectid import ObjectId

app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"])
db = client[app.config["DB_NAME"]]
listings_collection = db["listings"]

#helper funkcija
def format_datetime(dt):
    if dt:
        return dt.strftime("%d.%m.%Y. u %H:%M")
    return ""

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
            "created_at": datetime.now(UTC)
        }

        listings_collection.insert_one(listing)

        return redirect(url_for("home"))

    return render_template("create_listing.html")


@app.route("/listings")
def listings():
    selected_type = request.args.get("type", "all")
    location = request.args.get("location", "").strip()

    query = {}

    if selected_type == "owner":
        query["user_type"] = "owner"
    elif selected_type == "cleaner":
        query["user_type"] = "cleaner"

    if location:
        query["location"] = {"$regex": location, "$options": "i"}

    all_listings = list(listings_collection.find(query).sort("created_at", -1))

    for listing in all_listings:
        listing["formatted_created_at"] = format_datetime(listing.get("created_at"))

    return render_template(
        "listings.html",
        listings=all_listings,
        selected_type=selected_type,
        location=location
    )
    
@app.route("/listing/<listing_id>")
def listing_detail(listing_id):
    listing = listings_collection.find_one({"_id": ObjectId(listing_id)})

    if not listing:
        return "Oglas nije pronađen.", 404

    listing["formatted_created_at"] = format_datetime(listing.get("created_at"))

    return render_template("listing_detail.html", listing=listing)

@app.route("/admin")
def admin():
    all_listings = list(listings_collection.find().sort("created_at", -1))
    return render_template("admin.html", listings=all_listings)


@app.route("/delete-listing/<listing_id>", methods=["POST"])
def delete_listing(listing_id):
    listings_collection.delete_one({"_id": ObjectId(listing_id)})
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)