from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, URLField
from wtforms.validators import DataRequired
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app)
KEY = "8BYkEfBA6HlSihBXox7C0sKR6b"


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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class AddCafe(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = URLField("Map Location", validators=[DataRequired()])
    img_url = URLField("Image URL", validators=[DataRequired()])
    location = StringField("Cafe Locality", validators=[DataRequired()])
    seats = StringField("Seating Capacity", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price")
    has_toilet = BooleanField("Has Toilets")
    has_wifi = BooleanField("Has WiFi")
    has_sockets = BooleanField("Has Sockets")
    can_take_calls = BooleanField("Can Take Calls")
    submit = SubmitField('Submit')


class PriceUpdater(FlaskForm):
    coffee_price = StringField('New Price: ', validators=[DataRequired()])
    submit = SubmitField('Submit')



@app.route("/")
def home():
    all_cafes = db.session.query(Cafe).all()
    return render_template("index.html", cafes=all_cafes)


## HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = [random.choice(all_cafes)]
    return render_template("index.html", cafes=random_cafe)



@app.route("/search", methods=['GET', 'POST'])
def cafe_search():
    location = request.form['location']
    loc = str(location).lower()
    all_cafes = db.session.query(Cafe).all()
    cafes_in_loc = [cafe for cafe in all_cafes if str(cafe.location).lower() == loc]
    if len(cafes_in_loc) == 0:
        flash("No Cafes at this location")
    return render_template("index.html", cafes=cafes_in_loc)


## HTTP POST - Create Record
@app.route("/add", methods=['GET', 'POST'])
def add_cafe():
    form = AddCafe()
    if form.validate_on_submit():
        flash("New Cafe Added Successfully!", "message")
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH", 'GET', 'POST'])
def update_price(id):
    form = PriceUpdater()
    if form.validate_on_submit():
        all_cafes = db.session.query(Cafe).all()
        for cafe in all_cafes:
            if int(cafe.id) == int(id):
                cafe.coffee_price = form.coffee_price.data
                db.session.commit()
                flash("Price Updated Successfully")
                return redirect(url_for("home"))
                # return jsonify(response={"success": "Successfully updated the price."})
        # flash("Recheck your entry and try again.", "Error")
        # return jsonify(response={"Error": "Check your id and try again"})
    return render_template("update.html", form=form)


## HTTP DELETE - Delete Record


@app.route("/delete/<int:cafe_id>", methods=['GET', 'POST'])
def delete_cafe(cafe_id):
    # api_key = request.get["apiKey"]
    cafe = db.session.query(Cafe).get(cafe_id)
    # print(cafe)
    # if api_key != KEY:
    #     flash("Sorry! That's not allowed. Make sure you have the correct key", "Error")
    #     return redirect(url_for('home'))
    #     # return jsonify(response={"Error": "Sorry! That's not allowed. Make sure you have the correct key"})
    # else:
    db.session.delete(cafe)
    db.session.commit()
    flash("Cafe Deleted Successfully", "message")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
