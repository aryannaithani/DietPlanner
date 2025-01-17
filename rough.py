activity_level = {'sedentary': 1.2,
                  'light': 1.3,
                  'moderate': 1.5,
                  'heavy': 1.7,
                  'very heavy': 1.9}
gain_lose = {'maintain': 1,
             'mild loss': 0.9,
             'loss': 0.79,
             'extreme loss': 0.58,
             'mild gain': 1.1,
             'gain': 1.21,
             'fast gain': 1.42}

sex = input('Enter Your Gender: ')
age = int(input('Enter Your Age: '))
height = int(input('Enter Height: '))
weight = int(input('Enter Weight: '))
activity = input('Enter Activity Level: ')
goal = input('Enter weight gain or lose?: ')

calories = round((((10*weight) + (6.25*height) - (5*age) + 5) * activity_level.get(activity)) * gain_lose.get(goal))\
           if sex == 'm' else\
           round((((10 * weight) + (6.25 * height) - (5 * age) - 161) * activity_level.get(activity)) * gain_lose.get(goal))
print(calories)