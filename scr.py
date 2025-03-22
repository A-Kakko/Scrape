import requests

res = requests.get('https://www.orangepage.net/recipes')
print(res.text)
