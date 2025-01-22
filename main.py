from flask.views import MethodView
from wtforms import Form, StringField, SubmitField, validators, RadioField, SelectField
from flask import Flask
from flask import render_template, request
import requests

app = Flask(__name__)

class CalorieFormPage(MethodView):

    def __init__(self):
        self.calories = 0

    def get(self):
        form = CalorieForm()
        return render_template('form.html',
                               form=form)

    def post(self):
        form = CalorieForm(request.form)
        weight = float(form.weight.data)
        height = float(form.height.data)
        age = int(form.age.data)
        gender = form.gender.data
        activity = float(form.activity.data)
        goal = float(form.goal.data)

        self.calories = round((((10 * weight) + (6.25 * height) - (5 * age) + 5) * activity) * goal) \
            if gender == 'm' else \
            round((((10 * weight) + (6.25 * height) - (5 * age) - 161) * activity) * goal)

        return render_template('form.html',
                               form=form,
                               recipes=self.get_recipes(),
                               result=True)

    def get_recipes(self):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": '17318ba1b30e475bb39c7e643bb82ae0',  # Search query (e.g., ingredient or dish)
            "maxCalories": self.calories,  # Maximum calories
            "addRecipeInformation": True,
            "diet": "vegetarian",  # Include detailed recipe information
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])  # Return list of recipes
        elif response.status_code == 401:
            print("Unauthorized: Check your API key.")
            return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []


class CalorieForm(Form):
    weight = StringField('Weight (in kgs)',[validators.DataRequired()])
    age = StringField('Age',[validators.DataRequired()])
    height = StringField('Height (in cms)',[validators.DataRequired()])
    button = SubmitField("Count Intake 🥝", [validators.DataRequired()])
    gender = RadioField('Select Gender', [validators.DataRequired()], choices=[('m', 'Male'), ('f', 'Female')])
    activity = SelectField('Select an Activity Level', [validators.DataRequired()],
                                                            choices=[(1, 'Select'),
                                                                     (1.2, 'Sedentary'),
                                                                     (1.3, 'Light'),
                                                                     (1.5, 'Moderate'),
                                                                     (1.7, 'Heavy'),
                                                                     (1.9, 'Very Heavy')])
    goal = SelectField('Select a Weight Goal', [validators.DataRequired()],
                                                    choices=[(1, 'Select'),
                                                             (1, 'Maintain'),
                                                             (0.9, 'Mild Loss'),
                                                             (0.79, 'Loss'),
                                                             (0.58, 'Extreme Loss'),
                                                             (1.1, 'Mild Gain'),
                                                             (1.21, 'Gain'),
                                                             (1.42, 'Fast Gain')])


app.add_url_rule('/', view_func=CalorieFormPage.as_view('form_page'))

app.run(debug=True)