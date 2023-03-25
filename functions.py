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