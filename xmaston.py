import requests

import json


# Ваш токен
token = 'a1a34c48-b881-427a-858f-56c5982d68f5'
# URL сервера
server_url = 'https://games-test.datsteam.dev/play/snake3d'

# API-метод
api = '/player/move'
url = f"{server_url}{api}"

# Данные для отправки
data = {
    'snakes': []
}

# Заголовки запроса
headers = {
    'X-Auth-Token': token,
    'Content-Type': 'application/json'
}

# Выполнение POST-запроса
response = requests.post(url, headers=headers, json=data)

map_info = response.json()

# Координаты препядствий
fence_pos = map_info["fences"]

# Змейки
snake_1 = map_info["snakes"][0]
snake_2 = map_info["snakes"][1]
snake_3 = map_info["snakes"][2]

# Соперники
enemies = map_info["enemies"]


# еда
food = map_info["food"]

# специальная еда
special_food = map_info["specialFood"]

# ошибки
err = map_info["errors"]

print(snake_1)
print(food)



# Сохранение ответа в файл
with open('example_response.json', 'w') as file:
    file.write(response.text)