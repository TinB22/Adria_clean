from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from config import Config
from datetime import datetime, UTC
from bson.objectid import ObjectId
import certifi
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

ca = certifi.where()
client = MongoClient(app.config["MONGO_URI"], tlsCAFile=ca)
db = client[app.config["DB_NAME"]]
listings_collection = db["listings"]

app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

#nova kolekcija za korisnike
listings_collection = db["listings"]
users_collection = db["users"]
applications_collection = db["applications"]

#helper funkcija
def format_datetime(dt):
    if dt:
        return dt.strftime("%d.%m.%Y. u %H:%M")
    return ""

def is_admin_logged_in():
    return session.get("admin_logged_in", False)

def admin_required():
    if not is_admin_logged_in():
        flash("Prvo se moraš prijaviti kao admin.", "error")
        return False
    return True

def allowed_file(filename):
    allowed_extensions = {"png", "jpg", "jpeg", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

#helper f-je za login korisnika
def is_user_logged_in():
    return session.get("user_logged_in", False)

def current_user():
    if not is_user_logged_in():
        return None

    user_id = session.get("user_id")
    if not user_id:
        return None

    return users_collection.find_one({"_id": ObjectId(user_id)})

def user_required():
    if not is_user_logged_in():
        flash("Moraš se prijaviti za pristup ovoj stranici.", "error")
        return False
    return True

# BLOG - za DM
BLOG_POSTS = [
    {
        "slug": "kako-pronaci-pouzdanu-cistacicu-za-apartman-u-sezoni",
        "title": "Kako pronaći pouzdanu čistačicu za apartman u sezoni?",
        "category": "Savjeti za iznajmljivače",
        "date": "4.6.2026.",
        "image": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?q=80&w=1200&auto=format&fit=crop",
        "excerpt": "Turistička sezona donosi velik pritisak na vlasnike apartmana i vila. Saznajte kako na vrijeme organizirati čišćenje i izbjeći stres između smjena gostiju.",
        "content": """
Turistička sezona za vlasnike apartmana, vila i kuća za odmor često znači stalnu organizaciju, brzu komunikaciju i mnogo detalja koje treba uskladiti u kratkom vremenu. Jedan od najvećih izazova nastaje između odlaska jednih i dolaska drugih gostiju. U tom razdoblju objekt mora biti potpuno očišćen, provjeren i spreman za novi dolazak.

Pronalazak pouzdane osobe za čišćenje nije uvijek jednostavan. Mnogi vlasnici se oslanjaju na preporuke, poznanstva ili objave u Facebook grupama. Takav način može funkcionirati, ali često nije dovoljno brz ni pregledan, posebno kada se čišćenje mora organizirati u zadnji trenutak.

Pouzdana čistačica ili tim za čišćenje trebaju biti dostupni u dogovorenom terminu, razumjeti standarde turističkog smještaja i znati koliko je važno da objekt bude spreman prije dolaska novih gostiju. Vlasnicima je zato važno imati kanal putem kojeg mogu brzo pronaći osobe koje nude usluge čišćenja na njihovom području.

AdriaClean rješava taj problem povezivanjem vlasnika turističkih objekata s pružateljima usluga čišćenja. Vlasnik može objaviti potrebu, navesti lokaciju, opis objekta i termin, dok pružatelji usluga mogu pregledavati oglase ili objaviti vlastitu ponudu. Na taj način se proces pronalaska čišćenja pojednostavljuje i postaje pregledniji.

Najbolji savjet za vlasnike je da čišćenje ne organiziraju tek kada problem nastane. Potrebno je unaprijed definirati termine, imati rezervnu opciju i koristiti digitalne alate koji olakšavaju pronalazak dostupnih osoba. Tako se smanjuje stres, poboljšava kvaliteta usluge i osigurava bolji dojam kod gostiju.
"""
    },
    {
        "slug": "checklista-za-pripremu-vile-ili-apartmana-prije-dolaska-gostiju",
        "title": "Checklista za pripremu vile ili apartmana prije dolaska gostiju",
        "category": "Korisni resursi",
        "date": "4.6.2026.",
        "image": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?q=80&w=1200&auto=format&fit=crop",
        "excerpt": "Praktična checklista za vlasnike turističkih objekata koja pomaže da apartman ili vila budu spremni prije dolaska novih gostiju.",
        "content": """
Priprema apartmana ili vile prije dolaska gostiju jedan je od najvažnijih dijelova uspješnog turističkog iznajmljivanja. Gosti često prvi dojam stvaraju već pri ulasku u objekt, a čistoća je jedan od najvažnijih faktora zadovoljstva.

Kako bi se smanjila mogućnost pogreške, korisno je imati jednostavnu checklistu koja se može koristiti prije svakog dolaska gostiju.

1. Provjeriti kupaonice i sanitarije  
Kupaonice trebaju biti detaljno očišćene, bez tragova kamenca, neugodnih mirisa ili potrošenih osnovnih potrepština. Posebnu pažnju treba obratiti na WC školjku, tuš kabinu, umivaonik, ogledala i podove.

2. Zamijeniti posteljinu i ručnike  
Sva posteljina i ručnici moraju biti čisti, suhi i uredno složeni. Poželjno je imati rezervni set za situacije kada se smjene gostiju odvijaju u kratkom vremenu.

3. Očistiti kuhinju  
Kuhinju treba pregledati detaljno: radne površine, sudoper, hladnjak, štednjak, pećnicu, posuđe i ladice. Gosti često primjećuju sitne detalje, zato kuhinja mora ostavljati dojam urednosti.

4. Provjeriti podove i staklene površine  
Podovi, prozori, ogledala i staklene površine trebaju biti bez mrlja. Kod vila s bazenom i terasom važno je provjeriti i vanjske površine.

5. Nadopuniti osnovne potrepštine  
To uključuje sapun, toaletni papir, vrećice za smeće, deterdžent, spužvice i ostale osnovne stvari koje gosti očekuju.

6. Provjeriti klimu, Wi-Fi i rasvjetu  
Prije dolaska gostiju potrebno je provjeriti rade li klima uređaji, internet, televizor i rasvjeta. Sitni tehnički problemi mogu značajno utjecati na zadovoljstvo gostiju.

7. Fotografirati stanje objekta  
Fotografiranje objekta nakon čišćenja može pomoći vlasniku da ima dokaz o stanju prije dolaska gostiju.

Korištenjem ovakve checkliste vlasnici mogu smanjiti stres i povećati sigurnost da je objekt spreman za dolazak novih gostiju. AdriaClean dodatno olakšava ovaj proces jer omogućuje brže povezivanje s osobama koje nude usluge čišćenja.
"""
    },
    {
        "slug": "najcesce-greske-kod-organizacije-ciscenja-turistickog-objekta",
        "title": "Najčešće greške kod organizacije čišćenja turističkog objekta",
        "category": "Organizacija sezone",
        "date": "4.6.2026.",
        "image": "https://images.unsplash.com/photo-1563453392212-326f5e854473?q=80&w=1200&auto=format&fit=crop",
        "excerpt": "Loša organizacija čišćenja može dovesti do kašnjenja, nezadovoljnih gostiju i dodatnog stresa. Ovo su najčešće greške koje vlasnici mogu izbjeći.",
        "content": """
Organizacija čišćenja turističkog objekta često izgleda jednostavno, ali u praksi može postati jedan od najvećih izazova sezone. Kada gosti odlaze ujutro, a novi dolaze već poslijepodne, svaki detalj mora biti dobro isplaniran.

Prva česta greška je oslanjanje samo na jednu osobu za čišćenje. Ako ta osoba nije dostupna, kasni ili otkaže termin, vlasnik može imati ozbiljan problem. Zbog toga je korisno imati više mogućnosti i unaprijed znati kome se može obratiti.

Druga greška je nejasan dogovor oko opsega posla. Vlasnik i osoba koja čisti trebaju unaprijed dogovoriti što točno uključuje čišćenje: kupaonice, kuhinju, terasu, bazen, promjenu posteljine, pranje ručnika i provjeru osnovnih potrepština.

Treća greška je dogovaranje u zadnji trenutak. Iako se neke situacije ne mogu predvidjeti, većinu termina moguće je planirati ranije. Pravovremena organizacija smanjuje stres i omogućuje kvalitetniju uslugu.

Četvrta greška je komunikacija putem previše različitih kanala. Ako se dogovori vode kroz poruke, pozive, komentare u grupama i bilješke, lako dolazi do nesporazuma. Bolje je imati jasne informacije na jednom mjestu.

Peta greška je zanemarivanje povratnih informacija gostiju. Ako se gosti žale na čistoću, vlasnik treba reagirati odmah i poboljšati proces čišćenja prije sljedeće rezervacije.

AdriaClean pomaže u rješavanju ovih problema jer vlasnicima omogućuje objavu potrebe za čišćenjem, a pružateljima usluge daje prostor za predstavljanje. Time se komunikacija pojednostavljuje, a pronalazak usluge postaje brži i pregledniji.
"""
    }
]


@app.route("/")
def home():
    return render_template("index.html")

# ruta za BLOG
@app.route("/blog")
def blog():
    return render_template("blog.html", posts=BLOG_POSTS)


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = next((post for post in BLOG_POSTS if post["slug"] == slug), None)

    if not post:
        return "Blog objava nije pronađena.", 404

    return render_template("blog_detail.html", post=post)

#register i login rute za korisnike
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        if not full_name or not email or not password or not role:
            flash("Sva polja moraju biti ispunjena.", "error")
            return render_template("register.html")

        if role not in ["owner", "cleaner"]:
            flash("Neispravna uloga korisnika.", "error")
            return render_template("register.html")

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Korisnik s tim emailom već postoji.", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        user = {
            "full_name": full_name,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": datetime.now(UTC)
        }

        result = users_collection.insert_one(user)

        session["user_logged_in"] = True
        session["user_id"] = str(result.inserted_id)
        session["user_role"] = role
        session["user_name"] = full_name

        flash("Registracija je uspješna. Dobrodošao!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email i lozinka su obavezni.", "error")
            return render_template("login.html")

        user = users_collection.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            flash("Neispravan email ili lozinka.", "error")
            return render_template("login.html")

        session["user_logged_in"] = True
        session["user_id"] = str(user["_id"])
        session["user_role"] = user["role"]
        session["user_name"] = user["full_name"]

        flash("Uspješno si prijavljen.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_logged_in", None)
    session.pop("user_id", None)
    session.pop("user_role", None)
    session.pop("user_name", None)

    flash("Uspješno si odjavljen.", "success")
    return redirect(url_for("home"))

@app.route("/create-listing", methods=["GET", "POST"])
def create_listing():
    if not user_required():
        return redirect(url_for("login"))

    user = current_user()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        contact = request.form.get("contact", "").strip()
        image = request.files.get("image")

        if not title or not description or not location or not contact:
            flash("Sva polja moraju biti ispunjena.", "error")
            return render_template("create_listing.html")

        image_filename = None

        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Dozvoljeni su samo JPG, JPEG, PNG i WEBP formati.", "error")
                return render_template("create_listing.html")

            safe_filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            image.save(image_path)
            image_filename = unique_filename

        listing = {
            "title": title,
            "description": description,
            "user_type": user["role"],
            "user_id": user["_id"],
            "user_name": user["full_name"],
            "user_email": user["email"],
            "location": location,
            "contact": contact,
            "image_filename": image_filename,
            "created_at": datetime.now(UTC)
        }

        listings_collection.insert_one(listing)
        flash("Oglas je uspješno objavljen.", "success")
        return redirect(url_for("listings"))

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

#admin rute...
@app.route("/admin")
def admin():
    if not admin_required():
        return redirect(url_for("admin_login"))

    all_listings = list(listings_collection.find().sort("created_at", -1))

    for listing in all_listings:
        listing["formatted_created_at"] = format_datetime(listing.get("created_at"))

    return render_template("admin.html", listings=all_listings)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (
            username == app.config["ADMIN_USERNAME"]
            and password == app.config["ADMIN_PASSWORD"]
        ):
            session["admin_logged_in"] = True
            flash("Uspješno si prijavljen kao admin.", "success")
            return redirect(url_for("admin"))

        flash("Neispravno korisničko ime ili lozinka.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Uspješno si odjavljen.", "success")
    return redirect(url_for("home"))


@app.route("/delete-listing/<listing_id>", methods=["POST"])
def delete_listing(listing_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    listings_collection.delete_one({"_id": ObjectId(listing_id)})
    flash("Oglas je uspješno obrisan.", "success")
    return redirect(url_for("admin"))

@app.route("/edit-listing/<listing_id>", methods=["GET", "POST"])
def edit_listing(listing_id):
    if not admin_required():
        return redirect(url_for("admin_login"))

    listing = listings_collection.find_one({"_id": ObjectId(listing_id)})

    if not listing:
        return "Oglas nije pronađen.", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        user_type = request.form.get("user_type", "").strip()
        location = request.form.get("location", "").strip()
        contact = request.form.get("contact", "").strip()

        if not title or not description or not user_type or not location or not contact:
            flash("Sva polja moraju biti ispunjena.", "error")
            listing["title"] = title
            listing["description"] = description
            listing["user_type"] = user_type
            listing["location"] = location
            listing["contact"] = contact
            return render_template("edit_listing.html", listing=listing)

        updated_data = {
            "title": title,
            "description": description,
            "user_type": user_type,
            "location": location,
            "contact": contact,
        }

        listings_collection.update_one(
            {"_id": ObjectId(listing_id)},
            {"$set": updated_data}
        )

        flash("Oglas je uspješno ažuriran.", "success")
        return redirect(url_for("admin"))

    return render_template("edit_listing.html", listing=listing)



#krecem sa login korisnika


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
