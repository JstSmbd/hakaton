import requests
from random import choice


def add_help_btn(res):
    if "buttons" in res["response"]:
        res["response"]["buttons"].append(
            {
                "title": "Помощь",
                "hide": True
            }
        )
    else:
        res["response"]["buttons"] = [
            {
                "title": "Помощь",
                "hide": True
            }
        ]


def check_tokens(words, req):
    return any([word in req["request"]["nlu"]["tokens"] for word in words])


def get_location(req):
    location = {}
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            for key in set(entity['value'].keys()):
                if key not in location:
                    location[key] = entity["value"][key].title()
    # именно так, чтобы не было в адресе сразу два города или две улицы, то есть,
    # чтобы адреса были более реалистичными
    return ", ".join(list(location.values()))


def get_coords(address):
    response = requests.get("https://geocode-maps.yandex.ru/1.x/", {
        'geocode': address,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"
    })
    try:
        return response.json()["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]["Point"]["pos"].replace(" ", ",")
    except IndexError:
        return None


def get_restaurants(coords):
    if coords is None:
        return None
    response = requests.get("https://search-maps.yandex.ru/v1/", {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": "ресторан",
        "lang": "ru_RU",
        "ll": coords,
        "type": "biz"
    })
    org = response.json()["features"]
    return org


def rest_ask_btns():
    return [
        {
            "title": choice(["Давай этот", "Пойдет"]),
            "hide": True
        },
        {
            "title": choice(["Не, другой надо", "Другой"]),
            "hide": True
        }
    ]


def reset_smt(what, session):
    if what == "holiday":
        pass
    elif what == "recipe":
        session["recipe"]["key"] = None
        session["recipe"]["recipe"] = None
        session["recipe"]["ask_recipe"] = False
        session["recipe"]["say_recipe"] = False
        session["recipe"]["ask_right_recipe"] = False
    elif what == "restaurant":
        session["restaurant"]["i"] = 0
        session["restaurant"]["ask_info"] = False
        session["restaurant"]["change_rest"] = False


def get_recipe():
    # TODO: написать функцию
    return "котлеты", "рецепт котлет"


def get_holidays(dates):  # dates - список дат по типу: ["08.03", "09.03", "10.03"]
    # TODO: написать функцию
    return ["8 марта - международный женский день", "10 марта - чей-то день рождения"]


def get_facts(date):  # date - дата, например, "08.03"
    # TODO: написать функцию
    return "8 марта - женский день"


def get_dates(req):
    # TODO: написать функцию
    return ["08.03", "09.03", "10.03"]