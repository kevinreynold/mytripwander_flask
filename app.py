import json
import ast
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_
from flask_mail import Mail, Message #email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash #untuk encode password
from hotel import hotel_api

app = Flask(__name__)

app.config.from_pyfile('config.cfg')

CORS(app)
mail = Mail(app)
# from model import *

db = SQLAlchemy(app)
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
    has_airport = db.Column(db.Integer(), nullable=False)
    airport = db.Column(db.String(3), nullable=False)
    hotel_city_id = db.Column(db.String(255), nullable=False)

    places = db.relationship('Place', backref='city', lazy='dynamic')

    def __repr__(self):
        return '<Country %r>' % self.city_code

class Category(db.Model):
    __tablename__ = 'category_place'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    places = db.relationship('Place', backref='category_place', lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % self.id

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

class Interest(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return '<Interest %r>' % self.id

class Distance(db.Model):
    origin = db.Column(db.String(255), primary_key=True)
    destination = db.Column(db.String(255), primary_key=True)
    distance = db.Column(db.Integer(), nullable=False)
    travel_time = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return '<Distance %r>' % (str(self.origin) + ' - ' + str(self.destination))

#API
@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test", methods=['GET'])
def test():
    return jsonify({'message' : 'MANTAPPP!!'})

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter(User.email == data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        return jsonify({'message' : 'Login Sucess!!'})

    return jsonify({'message' : 'Login Failed!!'})

@app.route("/forgot/<email>", methods=['GET'])
def forgot_password(email):
    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify({'message' : 'Your request is submitted!'})

    msg = Message('Forgot Password', sender = app.config['MAIL_USERNAME'], recipients = [email])
    msg.body = "This is the email body" #kasih password baru
    mail.send(msg)
    return jsonify({'message' : 'Your request is submitted!', 'email' : email})

@app.route("/user/changepass", methods=['PUT'])
def change_password():
    data = request.get_json()
    user = User.query.filter(User.email == data['email']).first()

    if user and check_password_hash(user.password, data['old_password']):
        new_password = generate_password_hash(data['new_password'], method='sha256')
        user.password = new_password
        db.session.commit()
        return jsonify({'message' : 'Change Password Success!!'})

    return jsonify({'message' : 'Change Password Failed!!'})

@app.route("/user/register", methods=['POST'])
def register_user():
    data = request.get_json()

    #cek email dan username
    check_user = User.query.filter(User.email == data['email']).first()

    if check_user:
        return jsonify({'message' : 'Please use another email!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'Success register new user!'})

@app.route("/autocomplete/hotels", methods=['GET'])
def hotels_autocomplete():
    query = request.args.get('q')

    api = hotel_api(query=query)
    result = api.getListOfQueryResult()
    # api.save_result(result)

    return jsonify(result)

@app.route("/hotel/search", methods=['GET'])
def hotel_search():
    adults = request.args.get("adults")
    children = request.args.get("children")
    checkin = request.args.get("checkin")
    checkout = request.args.get("checkout")
    type = request.args.get("type")
    place_id = request.args.get("place_id")

    api = hotel_api(adults=adults, children=children, checkIn=checkin, checkOut=checkout)
    result = api.hotel_search(type, place_id)
    # api.save_result(result)

    return jsonify(result)

@app.route("/city/all", methods=['GET'])
def get_all_city():
    countries = Country.query.all()
    result = []
    for country in countries:
        temp = {}
        temp['country_code'] = country.country_code
        temp['country_name'] = country.country_name
        temp['cities'] = []
        cities = country.cities.all()
        for city in cities:
            temp2 = {}
            temp2['city_code'] = city.city_code
            temp2['city_name'] = city.city_name
            temp2['has_airport'] = city.has_airport
            temp2['hotel_city_id'] = city.hotel_city_id
            temp['cities'].append(temp2)
        result.append(temp)

    return jsonify({'result': result})

@app.route("/city/dest", methods=['GET'])
def get_city_destination():
    countries = Country.query.all()
    result = []
    for country in countries:
        temp = {}
        temp['country_code'] = country.country_code
        temp['country_name'] = country.country_name
        temp['total_city'] = len(country.cities.all())
        temp['cities'] = []
        cities = country.cities.filter(City.has_airport == 1).all()
        for city in cities:
            temp2 = {}
            temp2['city_code'] = city.city_code
            temp2['city_name'] = city.city_name
            temp2['has_airport'] = city.has_airport
            temp2['hotel_city_id'] = city.hotel_city_id
            temp['cities'].append(temp2)
        result.append(temp)

    return jsonify({'result': result})

@app.route("/airport/<city>", methods=['GET'])
def get_airport(city):
    city_code = '(' + city + ')'
    airport = Place.query.filter(Place.name.contains(city_code)).first()
    result = {
        'place_id' : airport.place_id,
        'category_id' : airport.category_id,
        'category_name' : airport.category_place.name,
        'city_code' : airport.city_code,
        'city_name' : airport.city.city_name,
        'latitude' : airport.latitude,
        'longitude' : airport.longitude,
        'name' : airport.name,
        'address' : airport.address,
        'phone_number' : airport.phone_number,
        'rating' : airport.rating,
        'reviews' : airport.reviews,
        'description' : airport.description,
        'avg_dur' : airport.avg_dur,
        'opening_hours' : ast.literal_eval(airport.opening_hours),
        'types' : airport.types,
        'interests' : airport.interests,
        'url' : airport.url,
        'photo_name' : airport.photo_name,
        'extension' : airport.extension,
        'misc' : airport.misc,
    }

    return jsonify({'result': result})

@app.route("/hotel/data/<hotel_id>", methods=['GET'])
def get_hotel_data(hotel_id):
    hotel = Place.query.filter(Place.misc == hotel_id).first()
    result = {
        'place_id' : hotel.place_id,
        'category_id' : hotel.category_id,
        'category_name' : hotel.category_place.name,
        'city_code' : hotel.city_code,
        'city_name' : hotel.city.city_name,
        'latitude' : hotel.latitude,
        'longitude' : hotel.longitude,
        'name' : hotel.name,
        'address' : hotel.address,
        'phone_number' : hotel.phone_number,
        'rating' : hotel.rating,
        'reviews' : hotel.reviews,
        'description' : hotel.description,
        'avg_dur' : hotel.avg_dur,
        'opening_hours' : ast.literal_eval(hotel.opening_hours),
        'types' : hotel.types,
        'interests' : hotel.interests,
        'url' : hotel.url,
        'photo_name' : hotel.photo_name,
        'extension' : hotel.extension,
        'misc' : hotel.misc,
    }

    return jsonify({'result': result})

@app.route("/airport/nearest/<city>", methods=['GET'])
def get_nearest_airport(city):
    airport = City.query.filter(City.city_code == city).first()
    result = airport.airport

    return jsonify({'result': result})

@app.route("/hotel/<city>", methods=['GET'])
def get_hotel(city):
    result = []
    hotels = Place.query.filter(Place.city_code == city).filter(Place.category_id == 4).all()
    for hotel in hotels:
        result.append(hotel.misc);

    return jsonify({'result': result, 'total': len(result)})

@app.route("/attraction/<city>", methods=['GET'])
def get_all_tourist_attraction(city):
    result = []
    attractions = Place.query.filter(Place.city_code == city).filter(Place.category_id == 2).order_by(desc(Place.reviews)).all()
    for attraction in attractions:
        temp = {
            'place_id' : attraction.place_id,
            'category_id' : attraction.category_id,
            'category_name' : attraction.category_place.name,
            'city_code' : attraction.city_code,
            'city_name' : attraction.city.city_name,
            'latitude' : attraction.latitude,
            'longitude' : attraction.longitude,
            'name' : attraction.name,
            'address' : attraction.address,
            'phone_number' : attraction.phone_number,
            'rating' : attraction.rating,
            'reviews' : attraction.reviews,
            'description' : attraction.description,
            'avg_dur' : attraction.avg_dur,
            'opening_hours' : ast.literal_eval(attraction.opening_hours),
            'types' : attraction.types,
            'interests' : attraction.interests,
            'url' : attraction.url,
            'photo_name' : attraction.photo_name,
            'extension' : attraction.extension,
            'misc' : attraction.misc,
        }
        result.append(temp);

    return jsonify({'result': result, 'total': len(result)})

@app.route("/food/<city>", methods=['GET'])
def get_all_food(city):
    result = []
    all_food = Place.query.filter(Place.city_code == city).filter(Place.category_id == 3).order_by(desc(Place.reviews)).all()
    for food in all_food:
        temp = {
            'place_id' : food.place_id,
            'category_id' : food.category_id,
            'category_name' : food.category_place.name,
            'city_code' : food.city_code,
            'city_name' : food.city.city_name,
            'latitude' : food.latitude,
            'longitude' : food.longitude,
            'name' : food.name,
            'address' : food.address,
            'phone_number' : food.phone_number,
            'rating' : food.rating,
            'reviews' : food.reviews,
            'description' : food.description,
            'avg_dur' : food.avg_dur,
            'opening_hours' : ast.literal_eval(food.opening_hours),
            'types' : food.types,
            'interests' : food.interests,
            'url' : food.url,
            'photo_name' : food.photo_name,
            'extension' : food.extension,
            'misc' : food.misc,
        }
        result.append(temp);

    return jsonify({'result': result, 'total': len(result)})

@app.route("/place/distance", methods=['GET'])
def get_distance():
    origin = request.args.get("origin")
    destination = request.args.get("destination")

    distance = Distance.query.filter(Distance.origin == origin).filter(Distance.destination == destination).first()
    if distance:
        result = {
            'origin' : distance.origin,
            'destination' : distance.destination,
            'travel_time' : distance.travel_time,
            'status' : 'Y'
        }
    else:
        result = {
            'origin' : origin,
            'destination' : destination,
            'travel_time' : 777,
            'status' : 'N'
        }

    return jsonify({'result': result})

@app.route("/place/nearby", methods=['GET'])
def get_nearby():
    origin = request.args.get("origin")
    distances = Distance.query.filter(Distance.origin == origin).order_by(Distance.travel_time).limit(20).all()
    result = []
    for distance in distances:
        place_id = distance.destination
        place = Place.query.filter(Place.place_id == place_id).filter(or_(Place.category_id == 2, Place.category_id == 3)).first()

        if place:
            temp = {
                'place_id' : place.place_id,
                'category_id' : place.category_id,
                'category_name' : place.category_place.name,
                'city_code' : place.city_code,
                'city_name' : place.city.city_name,
                'latitude' : place.latitude,
                'longitude' : place.longitude,
                'name' : place.name,
                'address' : place.address,
                'phone_number' : place.phone_number,
                'rating' : place.rating,
                'reviews' : place.reviews,
                'description' : place.description,
                'avg_dur' : place.avg_dur,
                'opening_hours' : ast.literal_eval(place.opening_hours),
                'types' : place.types,
                'interests' : place.interests,
                'url' : place.url,
                'photo_name' : place.photo_name,
                'extension' : place.extension,
                'misc' : place.misc,
                'travel_time' : distance.travel_time
            }
            result.append(temp);
        # else:
        #     temp = {
        #         'place_id' : distance.destination,
        #         'travel_time' : distance.travel_time
        #     }
        #     result.append(temp);

    return jsonify({'result': result, 'length': len(result)})

if __name__ == '__main__':
	app.run()
