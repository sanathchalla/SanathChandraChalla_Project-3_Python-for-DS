from sklearn.preprocessing import StandardScaler

ss = StandardScaler()
from flask import Flask
from flask import render_template, url_for, request, redirect, flash, session
import pickle
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
model = pickle.load(open('model.pk', 'rb'))

import pymysql

pymysql.install_as_MySQLdb()

app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = 'ItShouldBeALongStringOfRandomCharacters'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:AccessMySqlroot@localhost:3306/loan_approval'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))

    def __str__(self):
        return f"{self.username} has been registered successfully"


db.create_all()


@app.route('/', methods=['GET'])
def home():
    return render_template('Index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("Register.html")

    elif request.method == 'POST':
        valid_username = \
            User.query.filter(User.username == request.form.get('username')).first()

        if valid_username:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        else:
            new_credential = User(username=request.form.get('username'),
                                  password=request.form.get('password'))

            db.session.add(new_credential)
            db.session.commit()

            flash('User registered successfully', 'success')
            strn = url_for("register")

            print(strn)
            return redirect(strn)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("Login.html")

    elif request.method == 'POST':
        valid_credentials = \
            User.query.filter_by(username=request.form.get('username'), password=request.form.get('password')).first()
        if valid_credentials is not None:
            session['logged_in'] = True
            session['username'] = request.form.get('username')
            strn = url_for("enter_details")
            print(strn)
            return redirect(strn)
        else:
            flash('Invalid Username or Password')
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = ''
    return redirect(url_for('login'))


@app.route('/enter_details', methods=['GET'])
def enter_details():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return render_template("predict.html")


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template("predict.html")

    elif request.method == 'POST':
        Gender = request.form['Gender']
        Married = request.form['Married']
        Dependents = float(request.form['Dependents'])
        Education = request.form['Education']
        Self_employed = request.form['Self_employed']
        Applicant_Income = int(request.form['Applicant_Income'])
        Coapplicant_Income = float(request.form['Coapplicant_Income'])
        Loan_Amount = float(request.form['Loan_Amount'])
        Loan_Amount_Term = float(request.form['Loan_Amount_Term'])
        Credit_History = float(request.form['Credit_History'])
        Property_Area = request.form['Property_Area']

        prediction = model.predict([[Gender, Married, Dependents, Education, Self_employed, Applicant_Income,
                                     Coapplicant_Income, Loan_Amount, Loan_Amount_Term, Credit_History, Property_Area]])
        output = round(prediction[0], 1)
        if output >= 0.5:
            return render_template('predict.html',
                                   prediction_text='Congrats!! You are eligible for the loan.'.format(output))
        else:
            return render_template('predict.html',
                                   prediction_text='Sorry, you are not eligible for the loan.'.format(output))


if __name__ == "__main__":
    app.run(debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True