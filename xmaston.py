import requests
from sklearn.metrics.pairwise import manhattan_distances
import time

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

def escape_fence(fences,direction,geometry):
    all_direction_mass=[[-1,0,0],
                        [1,0,0],
                        [0,-1,0],
                        [0,1,0],
                        [0,0,-1],
                        [0,0,1]]
    #Если змея длинее 1 то назад нельзя двигаться 
    if (len(geometry))>1:
        all_direction_mass.pop(all_direction_mass.index([-x for x in direction]))
    #Убрать все направления что привидут уходу за границу
    for direction_mass in all_direction_mass:
        if any(x + y < 0 for x, y in zip(geometry[0], direction_mass*2)):
            all_direction_mass.pop(all_direction_mass.index(direction_mass))
    for fence in fences:
        dist_pixel_fence = manhattan_distances(fence,[geometry[0]])
        if 2 in dist_pixel_fence:            
            #До каких точек мало растояния
            distance_1 = [i for i, value in enumerate(dist_pixel_fence) if value == 2]            
            #Убрать все направления сталкновений с объектами
            for i in range(len(distance_1)):
                if [x + y for x, y in zip(geometry[0], direction*2)] == fence[distance_1[i]]:
                    all_direction_mass.pop(all_direction_mass.index(direction))                    
                    direction=all_direction_mass[0]
                    all_direction_mass.pop(0)
            #остановку можно убрать - тогда будут учитываться все преграды, но перебор займет больше времени
            break                    
    #Можно возращать весь набор возможных направлений 
    #return all_direction_mass
    return direction

def find_mandarin(foods, snake_coord, snakes_min_dist, special_foods=None):
    min_dist = 30_000
    min_coord = None
    for food in foods:
        if food["points"] > 0:
            dist = manhattan_distances([food["c"]],[snake_coord])
            if dist < min_dist:
                if len(snakes_min_dist) != 0 and food["c"] not in snakes_min_dist:
                    min_dist = dist
                    min_coord = food["c"]
                elif len(snakes_min_dist) == 0:
                    min_dist = dist
                    min_coord = food["c"]
    if special_foods is not None:
        min_gold_dist = 30_000
        for food in special_foods["golden"]:
            dist = manhattan_distances([food],[snake_coord])
            if dist < min_dist:
                if len(snakes_min_dist) != 0 and food not in snakes_min_dist:
                    min_dist = dist
                    min_coord = food
                    print("gold")
                elif len(snakes_min_dist) == 0:
                    min_dist = dist
                    min_coord = food
                    print("gold")
            if dist < min_gold_dist:
                min_gold_dist = dist

    print("dist", min_dist, min_gold_dist)
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
n = 4
previous_len = [0,0,0]
starttime = time.monotonic()
while True:
    print(k)
    if snakes is not None:
        min_coord_list = [0, 0, 0]
        for index, snake_1 in enumerate(snakes):
            if snake_1["status"] == "alive":
                snake_1_id = snake_1["id"]
                snake_1_dir = snake_1["direction"]
                snake_1_coord = snake_1["geometry"]
                if len(snake_1_coord) != previous_len[index]:
                    previous_len[index] = len(snake_1_coord)
                    min_coord = find_mandarin(food, snake_1_coord[0],min_coord_list, special_food)
                    min_coord_list[index] = min_coord
                dir = get_direction(min_coord_list[index], snake_1_coord[0])
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

    # специальная еда
    special_food = map_info["specialFood"]

    # ошибки
    err = map_info["errors"]
    for id, i in enumerate(snakes):
        if i["status"] != "alive":
            print(f"snake {id} is funny")
    #print(f"{snakes[0]['status']} \n {snakes[1]['status']} \n {snakes[2]['status']}")
    #print(food)

    # Сохранение ответа в файл
    with open(f'example/example_{n}_{k}_response.json', 'w') as file:
        file.write(response.text)
    k += 1
    time.sleep(1.0 - ((time.monotonic() - starttime) % 1.0))
