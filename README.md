# mytripwander_flask
Backend MyTripWander

Library yang perlu diinstall :
pip install Flask
pip install Flask-Mail
pip install Flask-SQLAlchemy
pip install flask-cors
pip install PyMySQL
pip install requests

Untuk membuat tabel pada database :
python
from app import db
db.drop_all()
db.create_all()

Untuk menjalankan virtualenv :
cd venv/Scripts
activate


Untuk menjalankan app:
python app.py
