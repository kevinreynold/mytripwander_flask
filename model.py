from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

#Tabel
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Country(db.Model):
    country_code = db.Column(db.String(2), primary_key=True)
    country_name = db.Column(db.String(45), nullable=False)

    cities = db.relationship('City', backref='country', lazy='dynamic')

    def __repr__(self):
        return '<Country %r>' % self.country_code

class City(db.Model):
    city_code = db.Column(db.String(3), primary_key=True)
    country_code = db.Column(db.String(2), db.ForeignKey('country.country_code'), nullable=False)
    city_name = db.Column(db.String(255), nullable=False)
    zone_id = db.Column(db.Integer(), nullable=False)
    has_airport = db.Column(db.Integer(), nullable=False)

    places = db.relationship('Place', backref='city', lazy='dynamic')

    def __repr__(self):
        return '<Country %r>' % self.city_code

class Category(db.Model):
    __tablename__ = 'category_place'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    places = db.relationship('Place', backref='category_place', lazy='dynamic')

class Place(db.Model):
    place_id = db.Column(db.String(255), primary_key=True)
    category_id = db.Column(db.Integer(), db.ForeignKey('category_place.id'), nullable=False)
    city_code = db.Column(db.String(3), db.ForeignKey('city.city_code'), nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longitude = db.Column(db.String(50), nullable=False)
    name = db.Column(db.Text(), nullable=False)
    address = db.Column(db.Text(), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    reviews = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    avg_dur = db.Column(db.Integer(), nullable=False)
    opening_hours = db.Column(db.Text(), nullable=False)
    types = db.Column(db.Text(), nullable=False)
    interests = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text(), nullable=False)
    photo_name = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    misc = db.Column(db.Text(), nullable=True)

    def __repr__(self):
        return '<Place %r>' % self.place_id
