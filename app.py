from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message #email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash #untuk encode password
from hotel import hotel_api

app = Flask(__name__)

app.config.from_pyfile('config.cfg')

CORS(app)
mail = Mail(app)
from model import *

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
    api.save_result(result)

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
            temp2['zone_id'] = city.zone_id
            temp2['has_airport'] = city.has_airport
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
            temp2['zone_id'] = city.zone_id
            temp2['has_airport'] = city.has_airport
            temp['cities'].append(temp2)
        result.append(temp)

    return jsonify({'result': result})

if __name__ == '__main__':
	app.run()
