import requests

# Replace with your Spoonacular API key
API_KEY = "17318ba1b30e475bb39c7e643bb82ae0"


def get_recipes(ingredient, max_calories):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": ingredient,  # Search query (e.g., ingredient or dish)
        "maxCalories": max_calories,  # Maximum calories
        "addRecipeInformation": True,
        "diet": "vegetarian",# Include detailed recipe information
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


# Example usage
ingredient = "broccoli"
max_calories = 500
recipes = get_recipes(ingredient, max_calories)

if recipes:
    for idx, recipe in enumerate(recipes, start=1):
        print(f"{idx}. {recipe['title']} - Recipe ID: {recipe['id']}")
        print(f"URL: {recipe.get('sourceUrl', 'No URL provided')}\n")
else:
    print("No recipes found or an error occurred.")
