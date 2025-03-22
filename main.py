from flask.views import MethodView
from wtforms import Form, StringField, SubmitField, validators, RadioField, SelectField
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_required, login_user

load_dotenv()
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

db_host = os.environ.get("DB_HOST", "trolley.proxy.rlwy.net")
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "VcNFNgolYhffcNEQlLhJvRanwESvXAeD")
db_name = os.environ.get("DB_NAME", "railway")
db_port = int(os.environ.get("DB_PORT", "57860"))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    if user_id:
        return User(user_id)  # Ensure it returns a valid object
    return None


class HomePage(MethodView):
    def get(self):
        return render_template('home.html')


class LoginView(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uinfo WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row and check_password_hash(row[1], password):
                flash('Login successful!', 'success')
                login_user(load_user(email))
                session['user_email'] = email
                session.pop('_flashes', None)
                cursor.close()
                conn.close()
                return redirect(url_for('form_page'))
            else:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))
        except pymysql.MySQLError as e:
            flash("Database connection error!", "danger")
            print("Database error:", e)
        return redirect(url_for('login'))


class SignupView(MethodView):
    def get(self):
        return render_template('signup.html')

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        try:
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uinfo WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row:
                flash('Email already registered. Please log in.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
            else:
                cursor.execute("INSERT INTO uinfo(email, password) VALUES (%s, %s)", (email, hashed_password))
                conn.commit()
                flash('Account created successfully! Please log in.', 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
        except pymysql.MySQLError as e:
            flash("Database connection error!", "danger")
            print("Database error:", e)
        return redirect(url_for('signup'))


class DashboardView(MethodView):
    @login_required
    def get(self):
        return "<h1>Welcome to your dashboard!</h1>"


class CalorieFormPage(MethodView):
    @login_required
    def get_recipes(self):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "maxCalories": session.get('calories', 2000),
            "addRecipeInformation": True,
            "diet": session.get('diet', ''),
        }
        response = requests.get(url, params=params)
        return response.json().get("results", []) if response.status_code == 200 else []

    @login_required
    def get(self):
        form = CalorieForm()
        return render_template('form.html', form=form, user=session['user_email'])

    @login_required
    def post(self):
        form = CalorieForm(request.form)
        weight = float(form.weight.data)
        height = float(form.height.data)
        age = int(form.age.data)
        gender = form.gender.data
        activity = float(form.activity.data)
        goal = float(form.goal.data)
        d_form = DietForm()

        calories = round((((10 * weight) + (6.25 * height) - (5 * age) + 5) * activity) * goal) if gender == 'm' else \
            round((((10 * weight) + (6.25 * height) - (5 * age) - 161) * activity) * goal)
        session['calories'] = calories

        try:
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE uinfo SET intake = %s WHERE email = %s", (calories, session['user_email']))
            conn.commit()
            cursor.close()
            conn.close()
        except pymysql.MySQLError as e:
            flash("Database error while updating intake!", "danger")
            print("Database error:", e)
        return render_template('form2.html', d_form=d_form, calories=calories, user=session['user_email'])


class DietFormPage(CalorieFormPage):
    @login_required
    def post(self):
        d_form = DietForm(request.form)
        session['diet'] = d_form.diet.data
        session['allergen'] = d_form.allergen.data
        recipes = self.get_recipes()
        return render_template('result.html', calories=session['calories'], recipes=recipes, type=session['diet'], allergen=session['allergen'], user=session['user_email'])


class CalorieForm(Form):
    weight = StringField('Weight (in kgs)', [validators.DataRequired()])
    age = StringField('Age', [validators.DataRequired()])
    height = StringField('Height (in cms)', [validators.DataRequired()])
    gender = RadioField('Select Gender', [validators.DataRequired()], choices=[('m', 'Male'), ('f', 'Female')])
    activity = SelectField('Select an Activity Level', [validators.DataRequired()],
                           choices=[(1.2, 'Sedentary'), (1.3, 'Light'), (1.5, 'Moderate'), (1.7, 'Heavy'),
                                    (1.9, 'Very Heavy')])
    goal = SelectField('Select a Weight Goal', [validators.DataRequired()],
                       choices=[(1, 'Maintain'), (0.9, 'Mild Loss'), (0.79, 'Loss'), (0.58, 'Extreme Loss'),
                                (1.1, 'Mild Gain'), (1.21, 'Gain'), (1.42, 'Fast Gain')])
    button = SubmitField("Count Intake 🥝")


class DietForm(Form):
    diet = SelectField('Select a Diet Type',
                       choices=[('', 'Not Specified'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan')])
    allergen = RadioField('Allergens', [validators.DataRequired()], choices=[('peanut', 'Peanuts'), ('gluten', 'Gluten')])
    button = SubmitField("Show Recipes")


app.add_url_rule('/counter', view_func=CalorieFormPage.as_view('form_page'))
app.add_url_rule('/diet-form', view_func=DietFormPage.as_view('diet_form_page'))
app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/signup', view_func=SignupView.as_view('signup'))
app.add_url_rule('/dashboard', view_func=DashboardView.as_view('dashboard'))
app.add_url_rule('/', view_func=HomePage.as_view('home_page'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port or default to 5000
    app.run(host="0.0.0.0", port=port)