import requests

url = 'https://api.telegram.org/bot6145953506:AAFBVZz8YptXkoBarbf2vXnxWHz1HQPEp7c/getUpdates'
params = {'offset': 0, 'timeout': 10}
response = requests.get(url, params=params)
#response = requests.get('https://google.com')
print(response)