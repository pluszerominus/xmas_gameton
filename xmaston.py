import requests
from sklearn.metrics.pairwise import manhattan_distances

import json


# Ваш токен
token = 'a1a34c48-b881-427a-858f-56c5982d68f5'
# URL сервера
server_url = 'https://games-test.datsteam.dev/play/snake3d'

# API-метод
api = '/player/move'
url = f"{server_url}{api}"

snake_1 = None

snake_1_dict = []
k = 0

def escape_fence(fences,direction,geometry):
    all_direction_mass=[[-1,0,0],
                   [1,0,0],
                   [0,-1,0],
                   [0,1,0],
                   [0,0,-1],
                   [0,0,1]]
    for fence in fences:
        for pixel_fence in fence:
            for i in range(len(all_direction_mass)):
                    if all_direction_mass[i]==direction:
                        all_direction_mass.pop(i)
                    break
            direction_mass=all_direction_mass
            while [x + y for x, y in zip(geometry[0], direction)] == pixel_fence:
                direction==direction_mass[0]
                direction_mass.pop(0)
    return direction

def find_mandarin(foods, snake_coord, special_foods=None):
    min_dist = 30_000
    min_coord = None
    for food in foods:
        if food["points"] > 0:
            dist = manhattan_distances([food["c"]],[snake_coord])
            if dist < min_dist:
                min_dist = dist
                min_coord = food["c"]

    for food in special_foods["golden"]:
        dist = manhattan_distances([food],[snake_coord])
        if dist < min_dist:
            min_dist = dist
            min_coord = food
            print("gold")


    print(min_dist)
    return min_coord

def get_direction(min_coord, head_coord):
    if head_coord[0] != min_coord[0]:
        if (min_coord[0] - head_coord[0]) > 0:
            return [1, 0, 0]
        else:
            return [-1, 0, 0]
    elif head_coord[1] != min_coord[1]:
        if (min_coord[1] - head_coord[1]) > 0:
            return [0, 1, 0]
        else:
            return [0, -1, 0]
    else:
        if (min_coord[2] - head_coord[2]) > 0:
            return [0, 0, 1]
        else:
            return [0, 0, -1]
n = 2
previous_len = None
while True:
    print(k)
    if snake_1 is not None:
        snake_1_id = snake_1["id"]
        snake_1_dir = snake_1["direction"]
        snake_1_coord = snake_1["geometry"]
        if len(snake_1_coord) != previous_len:
            previous_len = len(snake_1_coord)
            min_coord = find_mandarin(food, snake_1_coord[0])
        print(f"food - {min_coord}, snake - {snake_1_coord}")
        dir = get_direction(min_coord, snake_1_coord[0])
        print(dir)

        snake_1_dict = [{"id": snake_1_id, "direction": dir}]


    # Данные для отправки
    data = {
        'snakes': snake_1_dict
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

    print(f"{snake_1} \n {snake_2} \n {snake_3}")
    #print(food)

    # Сохранение ответа в файл
    with open(f'example/example_{n}_{k}_response.json', 'w') as file:
        file.write(response.text)
    k += 1