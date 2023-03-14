from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cafe_db_user:ihpgOftVY6vqTAp6iSbcgBYiUniNhQiL@dpg-cg8b38t269vf27frs0ug-a/cafe_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all():
    if request.method == "GET":
        cafes = db.session.query(Cafe).all()
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search", methods=["GET"])
def search():
    get_location = request.args.get('location')
    cafes = db.session.query(Cafe).all()
    list_out = []
    if request.method == "GET":
        for cafe in cafes:
            if cafe.location.lower() == get_location.lower():
                list_out.append(cafe.to_dict())
        if list_out:
            return jsonify(cafes=list_out)
        else:
            return {
                "error": {
                    "Not Found": f"Sorry we do not have a cafe location at {get_location}"
                }
            }


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=["PATCH"])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    new_price = request.args.get('new_price')
    if request.method == "PATCH":
        if cafe_to_update is not None:
            cafe_to_update.coffee_price = new_price
            db.session.commit()
            return jsonify({"success": "Successfully updated cafe price."})
        else:
            # 404 = Resource not found
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api_key = request.args.get('api-key')
    if request.method == "DELETE":
        if api_key == "TopSecretAPIKey":
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify({"success": "Successfully deleted cafe."})
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            return jsonify({"Error": "Sorry that is not allowed. Make sure that you have the correct API key"}), 404


if __name__ == '__main__':
    app.run(debug=True)
