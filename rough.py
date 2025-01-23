class DietForm(Form):
    diet = SelectField('Select a Diet Type', choices=[('', 'Not Specified'),
                                                          ('vegetarian', 'Vegetarian'),
                                                          ('vegan', 'Vegan')])
    button2 = SubmitField("Show Recipes", [validators.DataRequired()])

    def get_recipes(self):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": '17318ba1b30e475bb39c7e643bb82ae0',  # Search query (e.g., ingredient or dish)
            "maxCalories": self.calories,  # Maximum calories
            "addRecipeInformation": True,
            "diet": self.diet,  # Include detailed recipe information
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