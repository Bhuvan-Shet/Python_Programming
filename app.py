from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)


model = pickle.load(open("car_model.pkl", "rb"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username 
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/car')
def car():
    return render_template('car.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('uname')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        user = User(email=email, password=password, username=username, fname=fname, lname=lname)
        db.session.add(user)
        db.session.commit()
        flash('user has been registered successfully','success')
        return redirect('/login')
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect('/car')
        else:
            flash('Invalid Credentials', 'warning')
            return redirect('/login')
    return render_template("login.html")

@app.route('/predict1', methods = ['GET', 'POST'])
def predict1():
    int_features = [  x for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    i = prediction[0]
    return render_template('prediction.html', prediction_text=("%.2f" % round(i, 2)))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8081, debug=True)