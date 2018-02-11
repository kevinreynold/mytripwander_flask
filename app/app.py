from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message #email
from werkzeug.security import generate_password_hash, check_password_hash #untuk encode password

app = Flask(__name__)

app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
mail = Mail(app)

#Tabel
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

#API
@app.route("/")
def hello():
    return "Hello World!"

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

if __name__ == '__main__':
	app.run()
