from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice

app = Flask(__name__)

# Constants
API_KEY = "12345678"

# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# Return a random cafe
@app.route("/random", methods=['GET'])
def random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


# Return all cafes
@app.route("/all", methods=['GET'])
def all():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafes])


# Search for a cafe in a location
@app.route("/search", methods=['GET'])
def search():
    location = request.args.get("loc")  # Retrieves the value of parameter loc in the GET request
    # Returns a group of results for cafes where the entry location is the same as the passed location
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    # Creates a python list
    location_cafes = result.scalars().all()
    if location_cafes:  # Returns if search returns at least one cafe
        return jsonify(cafe=[cafe.to_dict() for cafe in location_cafes])
    else:  # Returns if search returns no cafes
        return jsonify(error={'Not Found': "Sorry, we don't have a cafe at that location."}), 404


# Add a cafe
@app.route("/add", methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form['name'],
        map_url=request.form['map_url'],
        img_url=request.form['img_url'],
        location=request.form['location'],
        seats=request.form['seats'],
        has_toilet=bool(request.form['has_toilet']),
        has_wifi=bool(request.form['has_wifi']),
        has_sockets=bool(request.form['has_sockets']),
        can_take_calls=bool(request.form['can_take_calls']),
        coffee_price=request.form['coffee_price']
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'Success': "Successfully added the new cafe"})


# Update price
@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    selected_cafe = db.session.get(Cafe, cafe_id)
    if selected_cafe:  # This will run if it successfully finds the cafe
        selected_cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(cafe=selected_cafe.to_dict()), 200
    else:
        return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database."}), 404


# Report Closed Cafe
@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def report_closed(cafe_id):
    api_key = request.args.get("api-key")
    cafe_to_delete = db.session.get(Cafe, cafe_id)
    if api_key == API_KEY:  # Checks if the users api key matches the one required to delete
        if cafe_to_delete:  # This will run if it successfully finds the cafe
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={'Success': "Successfully removed the cafe"}), 200
        else:  # Runs if no cafe with given id is found
            return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify({'Error': "Sorry , that's not allowed. Make sure you have the correct api_key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
