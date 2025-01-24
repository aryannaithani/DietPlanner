from flask.views import MethodView
from wtforms import Form, StringField, SubmitField, validators, RadioField, SelectField
from flask import Flask
from flask import render_template, request
import requests

app = Flask(__name__)
parameters = []

class CalorieFormPage(MethodView):

    def __init__(self, calories=0):
        self.calories = calories

    def get_recipes(self):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": '17318ba1b30e475bb39c7e643bb82ae0',  # Search query (e.g., ingredient or dish)
            "maxCalories": parameters[0],  # Maximum calories
            "addRecipeInformation": True,
            "diet": parameters[1],  # Include detailed recipe information
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
        d_form = DietForm()

        self.calories = round((((10 * weight) + (6.25 * height) - (5 * age) + 5) * activity) * goal) \
            if gender == 'm' else \
            round((((10 * weight) + (6.25 * height) - (5 * age) - 161) * activity) * goal)

        parameters.append(self.calories)

        return render_template('form2.html',
                               d_form=d_form,
                               calories=self.calories)


class DietFormPage(CalorieFormPage):

    def get(self):
        d_form = DietForm()
        return render_template('form2.html',
                               d_form=d_form,
                               calories=self.calories)

    def post(self):
        d_form = DietForm(request.form)
        diet = d_form.diet.data
        parameters.append(diet)
        recipes = self.get_recipes()
        return render_template('result.html',
                               d_form=d_form,
                               result=True,
                               diet=diet,
                               calories=self.calories,
                               recipes=recipes)


class CalorieForm(Form):
    weight = StringField('Weight (in kgs)',[validators.DataRequired()])
    age = StringField('Age',[validators.DataRequired()])
    height = StringField('Height (in cms)',[validators.DataRequired()])
    button = SubmitField("Count Intake 🥝", [validators.DataRequired()])
    gender = RadioField('Select Gender', [validators.DataRequired()], choices=[('m', 'Male'), ('f', 'Female')])
    activity = SelectField('Select an Activity Level', [validators.DataRequired()],
                                                            choices=[(1, '--Select--'),
                                                                     (1.2, 'Sedentary'),
                                                                     (1.3, 'Light'),
                                                                     (1.5, 'Moderate'),
                                                                     (1.7, 'Heavy'),
                                                                     (1.9, 'Very Heavy')])
    goal = SelectField('Select a Weight Goal', [validators.DataRequired()],
                                                    choices=[(1, '--Select--'),
                                                             (1, 'Maintain'),
                                                             (0.9, 'Mild Loss'),
                                                             (0.79, 'Loss'),
                                                             (0.58, 'Extreme Loss'),
                                                             (1.1, 'Mild Gain'),
                                                             (1.21, 'Gain'),
                                                             (1.42, 'Fast Gain')])


class DietForm(Form):
    diet = SelectField('Select a Diet Type', choices=[('', 'Not Specified'),
                                                          ('vegetarian', 'Vegetarian'),
                                                          ('vegan', 'Vegan')])
    button = SubmitField("Show Recipes", [validators.DataRequired()])


app.add_url_rule('/', view_func=CalorieFormPage.as_view('form_page'))
app.add_url_rule('/diet-form', view_func=DietFormPage.as_view('diet_form_page'))

app.run(debug=True)