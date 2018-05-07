import json
import ast # ast.literval_eval()
import string
from random import *
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_
from flask_mail import Mail, Message #email
from flask_cors import CORS
from datetime import datetime
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
    currency_id = db.Column(db.String(3), db.ForeignKey('currency.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    trips = db.relationship('Trip', backref='user', lazy='dynamic')

    tripschedules = db.relationship('Tripschedule', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

class Currency(db.Model):
    id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    rate = db.Column(db.Float(), nullable=False)

    users = db.relationship('User', backref='currency', lazy='dynamic')

    def __repr__(self):
        return '<Currency %r>' % self.id

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

class Trip(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    plan_data = db.Column(db.Text(), nullable=False)
    city_plan_data = db.Column(db.Text(), nullable=False)
    flight_data = db.Column(db.Text(), nullable=False)
    total_budget = db.Column(db.Float(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return '<Trip %r>' % (str(self.id))

class Tripschedule(db.Model):
    schedule_id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    plan_data = db.Column(db.Text(), nullable=False)
    is_done = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False)
    done_at = db.Column(db.DateTime(), nullable=True)

    def __repr__(self):
        return '<Tripschedule %r>' % (str(self.schedule_id))

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
        new_user = {
            'id': user.id,
            'currency_id': user.currency_id,
            'username': user.username
        }
        return jsonify({'message' : 'Login Success..', 'user': new_user, 'status': 'OK'})

    return jsonify({'message' : 'Login Failed..', 'status': 'NO'})

@app.route("/forgot/<email>", methods=['GET'])
def forgot_password(email):
    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify({'message' : 'Your request is submitted!'})

    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.digits
    new_password = "".join(choice(allchar) for x in range(randint(min_char, max_char)))

    new_password_encrypted = generate_password_hash(new_password, method='sha256')
    user.password = new_password_encrypted
    db.session.commit()

    msg = Message('Forgot Password', sender = app.config['MAIL_USERNAME'], recipients = [email])
    msg.html = "<h2>Your password has been reset</h2><br> <h3>Dear " + user.username + ",<br><br> Your account password has been reset. Please use the following temporary password to log in.<br><br> Your temporary password : <b>" + new_password + "</b></h3>"#kasih password baru
    mail.send(msg)
    return jsonify({'message' : 'Your request is submitted!', 'email' : email, 'password' : new_password})

@app.route("/user/changepass", methods=['POST'])
def change_password():
    data = request.get_json()
    user = User.query.filter(User.email == data['email']).first()

    if user and check_password_hash(user.password, data['old_password']):
        new_password = generate_password_hash(data['new_password'], method='sha256')
        user.password = new_password
        db.session.commit()
        return jsonify({'message' : 'Change Password Success!!', 'status' : 'OK'})

    return jsonify({'message' : 'Change Password Failed!!', 'status' : 'NO'})

@app.route("/user/register", methods=['POST'])
def register_user():
    data = request.get_json()

    #cek email dan username
    check_user = User.query.filter(User.email == data['email']).first()

    if check_user:
        return jsonify({'message' : 'Email address is already taken.', 'status' : 'NO'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, email=data['email'], currency_id=data['currency_id'])
    db.session.add(new_user)
    db.session.commit()

    new_user_id = User.query.filter(User.email == data['email']).first().id

    return jsonify({'message' : 'Success register new user.', 'status' : 'OK', 'user_id': new_user_id})

@app.route("/currency", methods=['GET'])
def get_all_currency():
    currencies = Currency.query.all()
    result = []
    for currency in currencies:
        temp = {
            'id': currency.id,
            'name': currency.name,
            'symbol': currency.symbol
        }
        result.append(temp)

    return jsonify({'result': result})

@app.route("/currency/update", methods=['POST'])
def update_currency():
    data = request.get_json()

    user = User.query.filter(User.id == data['user_id']).first()
    user.currency_id = data['currency_id']

    db.session.commit()

    return jsonify({'message' : 'Success update currency!'})

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
        'opening_hours' : json.loads(airport.opening_hours),
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
        'opening_hours' : json.loads(hotel.opening_hours),
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
            'opening_hours' : json.loads(attraction.opening_hours),
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
            'opening_hours' : json.loads(food.opening_hours),
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
                'opening_hours' : json.loads(place.opening_hours),
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

@app.route("/trip/auto", methods=['POST'])
def save_auto_trip():
    data = request.get_json()
    created_at = datetime.now().replace(microsecond=0)

    new_trip_schedule = Tripschedule(user_id=data['user_id'], plan_data=data['plan_data'], is_done=0, description=data['description'], created_at=created_at, done_at=None)
    db.session.add(new_trip_schedule)
    db.session.commit()

    #cari trip idnya berdasarkan created_at
    return jsonify({'message' : 'Success save new auto trip!'})

@app.route("/trip/save", methods=['POST'])
def save_trip():
    data = request.get_json()
    created_at = datetime.now().replace(microsecond=0)

    new_trip = Trip(user_id=data['user_id'], plan_data=data['plan_data'], city_plan_data=data['city_plan_data'], flight_data=data['flight_data'], total_budget=data['total_budget'], created_at=created_at)
    db.session.add(new_trip)
    db.session.commit()

    #cari trip idnya berdasarkan created_at
    trip = Trip.query.filter(Trip.created_at == created_at).filter(Trip.user_id == data['user_id']).first()

    return jsonify({'message' : 'Success save new trip!', 'trip_id' : trip.id})

@app.route("/trip/update", methods=['POST'])
def update_trip():
    data = request.get_json()

    trip = Trip.query.filter(Trip.id == data['trip_id']).first()
    trip.plan_data = data['plan_data']
    trip.city_plan_data = data['city_plan_data']
    trip.flight_data = data['flight_data']
    trip.total_budget = data['total_budget']

    db.session.commit()

    return jsonify({'message' : 'Success update trip!'})

@app.route("/trip/load/all", methods=['GET'])
def load_trip_list():
    user_id = int(request.args.get("user_id"))
    trips = Trip.query.filter(Trip.user_id == user_id).order_by(desc(Trip.created_at)).all()
    result = []
    for trip in trips:
        temp = {
            'id': trip.id,
            'plan_data': json.loads(trip.plan_data),
            'total_budget': trip.total_budget,
            'created_at': trip.created_at
            # 'plan_data': trip.plan_data
        }
        result.append(temp);

    return jsonify({'result': result, 'total': len(result)})

@app.route("/trip/load/<id>", methods=['GET'])
def load_trip(id):
    trip = Trip.query.filter(Trip.id == id).first()
    result = {
        'id': trip.id,
        'plan_data': json.loads(trip.plan_data),
        'city_plan_data': json.loads(trip.city_plan_data),
        'flight_data': json.loads(trip.flight_data),
        'total_budget': trip.total_budget,
        'created_at': trip.created_at
    }

    return jsonify({'result': result, 'total': len(result)})

@app.route("/currency/<id>", methods=['GET'])
def get_currency_value(id):
    currency = Currency.query.filter(Currency.id == id.upper()).first()
    result = {
        'name': currency.name,
        'symbol': currency.symbol,
        'rate': currency.rate,
    }

    return jsonify({'result': result})


if __name__ == '__main__':
	app.run()
