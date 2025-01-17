import requests
from selectorlib import Extractor

sex = input('Enter Your Gender: ')
age = input('Enter Your Age: ')
height = input('Enter Height: ')
weight = input('Enter Weight: ')

req = requests.get(f'https://www.calculator.net/bmr-calculator.html?cage={age}&'
                   f'csex={sex}&'
                   f'cheightmeter={height}&'
                   f'ckg={weight}&'
                   f'cmop=0&coutunit=c&cformula=m&cfatpct=20&ctype=metric&x=Calculate')

extractor = Extractor.from_yaml_file('calorie.yaml')
calories = extractor.extract(req.text)['calorie']
print(calories)