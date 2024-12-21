import requests
from sklearn.metrics.pairwise import manhattan_distances
import time
import numpy as np

import json


# Ваш токен
token = 'a1a34c48-b881-427a-858f-56c5982d68f5'
# URL сервера
server_url = 'https://games-test.datsteam.dev/play/snake3d'

# API-метод
api = '/player/move'
url = f"{server_url}{api}"

snakes = None

snake_1_dict = []
k = 0

def check_free_place(snake_coord, food, fences):
    all_direction_mass=[[-1,0,0],
                        [1,0,0],
                        [0,-1,0],
                        [0,1,0],
                        [0,0,-1],
                        [0,0,1]]
    min_dist = 30_000
    for i in all_direction_mass:
        dist = manhattan_distances([food], [snake_coord[0] + i])
        if snake_coord[0] + i not in fences and dist < min_dist:
            dir = i
            min_dist = dist

    return dir

def get_safe_dir(snake_dir, snake_coord, food, fences):
    if len(snake_coord) > 1:
        for coord in range(1,len(snake_coord)):
            fences.append(snake_coord[coord])
    all_direction_mass = [[-1, 0, 0],
                          [1, 0, 0],
                          [0, -1, 0],
                          [0, 1, 0],
                          [0, 0, -1],
                          [0, 0, 1]]
    min_dist = 30_000
    dir = snake_dir
    snake_coord = np.array(snake_coord)
    if list(np.array(snake_dir)*2 + snake_coord[0]) in fences:
        for i in all_direction_mass:
            dist = manhattan_distances([food], [snake_coord[0] + i])
            if list(snake_coord[0] + i) not in fences and dist < min_dist:
                dir = i
                min_dist = dist
    if dir != snake_dir:
        print(f"Change direction {snake_dir} to {dir}")

    return list(dir)


def find_gold(snake_coord, snakes_min_dist, special_foods):
    min_dist = 30_000
    min_coord = -1
    if len(special_foods) == 0:
        return -1
    min_gold_dist = 30_000
    for food in special_foods["golden"]:
        dist = manhattan_distances([food],[snake_coord])
        if dist < min_dist:
            if len(snakes_min_dist) != 0 and food not in snakes_min_dist:
                min_dist = dist
                min_coord = food
            elif len(snakes_min_dist) == 0:
                min_dist = dist
                min_coord = food
        if dist < min_gold_dist:
            min_gold_dist = dist

    print("dist", min_dist, min_gold_dist)
    return min_coord

def find_mandarin(foods, snake_coord, snakes_min_dist, center):
    min_dist = 30_000
    min_coord = None
    extra_min_coord = None
    min_extra = 30_000
    for food in foods:
        if food["points"] > 0:
            dist = manhattan_distances([food["c"]],[snake_coord])
            world_center_dist = manhattan_distances([center], [food["c"]])
            if dist < min_dist and world_center_dist <= 100:
                if len(snakes_min_dist) != 0 and food["c"] not in snakes_min_dist:
                    min_dist = dist
                    min_coord = food["c"]
                elif len(snakes_min_dist) == 0:
                    min_dist = dist
                    min_coord = food["c"]
            elif dist < min_extra:
                if len(snakes_min_dist) != 0 and food["c"] not in snakes_min_dist:
                    min_extra = dist
                    extra_min_coord = food["c"]
                elif len(snakes_min_dist) == 0:
                    min_extra = dist
                    extra_min_coord = food["c"]
    if min_coord is None:
        return extra_min_coord
    else:
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

n = 6

previous_len = [0,0,0]
min_coord_list = [0, 0, 0]
gold_snake_id = -1
previous_turn = -1
previous_dist = -1
min_coord = -1

while True:
    print(k)
    if snakes is not None and previous_turn != current_turn:
        previous_turn = current_turn
        world_center = (map_size // 2)
        for index, snake_1 in enumerate(snakes):
            if snake_1["status"] == "alive":
                if gold_snake_id == -1:
                    dist = manhattan_distances([world_center], [snake_1["geometry"][0]])
                    if dist > previous_dist:
                        previous_dist = dist
                        m = index
        gold_snake_id = m

        for index, snake_1 in enumerate(snakes):
            if snake_1["status"] == "alive":
                snake_1_id = snake_1["id"]
                snake_1_dir = snake_1["direction"]
                snake_1_coord = snake_1["geometry"]
                if len(snake_1_coord) != previous_len[index] or min_coord_list[index] not in food_coord:
                    previous_len[index] = len(snake_1_coord)
                    if index != gold_snake_id:
                        min_coord = find_mandarin(food, snake_1_coord[0],min_coord_list, world_center)
                    else:
                        min_coord = find_gold(snake_1_coord[0], min_coord_list, special_food)
                        if min_coord == -1:
                            min_coord = find_mandarin(food, snake_1_coord[0], min_coord_list, world_center)
                    min_coord_list[index] = min_coord
                print(min_coord_list[index], snake_1_coord[0])
                dir = get_direction(min_coord_list[index], snake_1_coord[0])
                dir = get_safe_dir(dir, snake_1_coord, min_coord_list[index], fence_pos)


                print(f"For snakes_{index}: food - {min_coord_list[index]}, snake - {snake_1_coord}, dir - {dir}")
                snake_1_dict.append({"id": snake_1_id, "direction": dir})
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

    map_size = np.array(map_info["mapSize"],dtype=int)
    # Координаты препядствий
    fence_pos = map_info["fences"]

    # Змейки
    snakes = map_info["snakes"]
    # snake_2 = map_info["snakes"][1]
    # snake_3 = map_info["snakes"][2]

    # Соперники
    enemies = map_info["enemies"]

    # еда
    food = map_info["food"]
    food_coord = [val["c"] for val in food]

    # специальная еда
    special_food = map_info["specialFood"]

    # ошибки
    err = map_info["errors"]

    current_turn = map_info["turn"]
    for id, i in enumerate(snakes):
        if i["status"] != "alive":
            print(f"snake {id} is funny")
    #print(f"{snakes[0]['status']} \n {snakes[1]['status']} \n {snakes[2]['status']}")
    #print(food)

    # Сохранение ответа в файл
    with open(f'example/example_{n}_{k}_response.json', 'w') as file:
        file.write(response.text)
    k += 1
    time.sleep(0.1)

