from flask import Flask, request, jsonify
import json
from flask_ngrok import run_with_ngrok
from functions import add_help_btn, check_tokens, get_location, get_coords, get_restaurants, \
    rest_ask_btns, get_recipe, reset_smt, get_dates, get_facts, get_holidays

app = Flask(__name__)
run_with_ngrok(app)
sessionStorage = {}

# TODO: сделать разные варианты ответов на одни и те же вопросы
# TODO: разобраться с интентами, я так понимаю это что-то нужно, хотя толком и не знаю, что это


actions_buttons = [
    {
        "title": "Какой сегодня праздник?",
        "hide": True
    },
    {
        "title": "Что мне приготовить?",
        "hide": True
    },
    {
        "title": "Где мне поесть?",
        "hide": True
    }
]
recipe_btns = [
    {
        "title": "Давай",
        "hide": True
    },
    {
        "title": "Не, другое",
        "hide": True
    }
]


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    user_id = request.json['session']['user_id']
    handle_dialog(response, request.json, user_id)
    sessionStorage[user_id]["last_buttons"] = response["response"].get("buttons", []).copy()
    add_help_btn(response)
    return jsonify(response)


def handle_dialog(res, req, user_id):
    if req['session']['new']:
        sessionStorage[user_id] = {
            "state": None,
            "restaurant": {
                "i": 0,
                "orgs": None,
                "ask_info": False,
                "change_rest": False
            },
            "recipe": {
                "key": None,
                "recipe": None,
                "ask_recipe": False,
                "say_recipe": False,
                "ask_right_recipe": False
            },
            "holiday": {

            }
        }
        res["response"]["text"] = "Здесь должна была быть картинка, но ее нет"
        res["response"]["card"] = {"type": "BigImage",
                                   "image_id": "1540737/2ed60101ba34854fddbb",
                                   "title": "С добрым утром! Вы хотите узнать какой сегодня праздник, "
                                            "что приготовить на завтрак или, может, куда сходить поесть?"}
        res["response"]["buttons"] = actions_buttons.copy()
        return
    session = sessionStorage[user_id]
    state = session["state"]
    if check_tokens(["помощь", "помоги"], req):
        res["response"]["text"] = "Я могу помочь тебе приготовить завтрак, " \
                                  "решить куда сходить поесть или сказать какой сегодня праздник."
        btns = actions_buttons.copy()
        btns.extend(session["last_buttons"].copy())
        res["response"]["buttons"] = btns
    elif check_tokens(["что"], req) and check_tokens(["умеешь"], req):
        res["response"]["text"] = "Я могу сказать какой будет праздник, " \
                                  "в названную вами дату, сказать что и как вам приготовить или " \
                                  "сказать в какой ресторан вам сходить."
        btns = actions_buttons.copy()
        btns.extend(session["last_buttons"].copy())
        res["response"]["buttons"] = btns
    elif check_tokens(["какой", "какие", "что", "расскажи", "скажи"], req) and \
            check_tokens(["праздник", "праздники"], req):
        session["state"] = "holiday"
        holiday(res, req, session)
    elif check_tokens(["позавтракать", "поесть", "пообедать", "поужинать", "приготовить"], req) and \
            check_tokens(["что"], req):
        session["state"] = "recipe"
        reset_smt("recipe", session)
        recipe(res, req, session)
    elif check_tokens(["позавтракать", "поесть", "пообедать", "поужинать"], req) and \
            check_tokens(["где"], req):
        session["state"] = "restaurant"
        reset_smt("restaurant", session)
        restaurant(res, req, session, True)
    elif state:
        if state == "holiday":
            holiday(res, req, session)
        elif state == "recipe":
            recipe(res, req, session)
        else:
            restaurant(res, req, session)
    elif check_tokens(["хватит", "достаточно", "пока"], req):
        res["response"]["text"] = "До встречи!"
        res["response"]["end_session"] = True
    else:
        res["response"]["text"] = "Что, не поняла вас?"
        res["response"]["buttons"] = session["last_buttons"]


def holiday(res, req, ses):
    # TODO: проверить функцию
    if (check_tokens(["расскажи", "скажи"], req) and check_tokens(["про", "о"], req)) or \
            check_tokens(["еще"], req):
        facts = get_facts(get_dates(req)[0])
        if facts:
            res["response"]["text"] = f"{facts}, вам еще что-нибудь рассказать про этот праздник?"
            res["response"]["buttons"] = [
                {
                    "title": "Расскажи еще",
                    "hide": True
                }
            ]
        else:
            res["response"]["text"] = "Я не знаю ничего про этот праздник"
    elif check_tokens(["хватит", "достаточно", "нет", "не надо"], req):
        ses["state"] = None
        res["response"]["text"] = "Хорошо. Так что вы хотите: узнать еще что-нибудь про " \
                                  "праздники, сходить куда-нибудь или приготовить еду?"
        res["response"]["buttons"] = actions_buttons.copy()
    else:
        holidays = get_holidays(get_dates(req))
        if holidays:
            holidays = '\n'.join(holidays)
            res["response"][
                "text"] = f"{holidays}!\nВам рассказать что-то про какой-нибудь праздник или может сказать какой праздник в другую дату?"
        else:
            res["response"][
                "text"] = "К сожалению либо в это время нет праздников, либо я таких не знаю, " \
                          "может вы хотите узнать что-нибудь про другую дату?"


def recipe(res, req, ses):
    # TODO: проверить функцию
    rec = ses["recipe"]
    if not rec["ask_recipe"] and not rec["say_recipe"]:
        rec["key"], rec["recipe"] = get_recipe()
        res["response"]["text"] = f"Как вам {rec['key']}, рассказать рецепт или что-нибудь другое?"
        rec["ask_recipe"] = True
        res["response"]["buttons"] = recipe_btns.copy()
    elif rec["ask_recipe"]:
        if check_tokens(["расскажи", "рассказывай", "давай", "этот"], req):
            rec["say_recipe"] = True
            rec["ask_recipe"] = False
            recipe(res, req, ses)
        elif check_tokens(["другой", "меняй", "другое"], req):
            rec["ask_recipe"] = False
            recipe(res, req, ses)
        else:
            res["response"]["text"] = "Не поняла вас..."
            res["response"]["buttons"] = ses["last_buttons"].copy()
    elif rec["say_recipe"] and not rec["ask_right_recipe"]:
        res["response"]["text"] = f"Ну что ж: {rec['recipe']}, будете готовить?"
        rec["ask_right_recipe"] = True
        res["response"]["buttons"] = recipe_btns.copy()
    elif rec["ask_right_recipe"]:
        if check_tokens(["да", "пойдет", "давай", "подходит"], req):
            res["response"]["text"] = "Удачи! А не хотите узнать есть ли сегодня праздник, " \
                                      "приготовить что-нибудь другое или пойти ресторан?"
            reset_smt("recipe", ses)
            ses["state"] = None
            res["response"]["buttons"] = actions_buttons.copy()
        elif check_tokens(["нет", "другое", "меняй"], req):
            rec["ask_recipe"] = False
            rec["say_recipe"] = False
            recipe(res, req, ses)
        else:
            res["response"]["text"] = "Не поняла вас..."
            res["response"]["buttons"] = ses["last_buttons"].copy()
    else:
        res["repsonse"]["text"] = "Что-то пошло не так..."
        # по идее до сюда программа не должна доходить вообще


def restaurant(res, req, ses, first=False):
    # TODO: проверить функцию
    # TODO: сделать возможность узнать геолокацию пользователя, не спрашивая напрямую
    rest = ses["restaurant"]
    try:
        if not rest["orgs"] and (location := get_location(req)) and (coords := get_coords(location)):
            rest["orgs"] = get_restaurants(coords)
            # пусть координаты пользователя не будут меняться во время взаимодействия
            restaurant(res, req, ses)
        elif not rest["orgs"]:
            res["response"]["text"] = ("" if first else "Я вас не поняла. ") + "Где вы находитесь?"
        elif rest["orgs"] and not rest["ask_info"] and not rest["change_rest"]:
            res["response"]["text"] = f"Вы можете пойти в ресторан " \
                                      f"\"{rest['orgs'][rest['i']]['properties']['CompanyMetaData']['name']}\", находящийся по адресу " \
                                      f"\"{rest['orgs'][rest['i']]['properties']['CompanyMetaData']['address']}\", хотите узнать про него побольше или может хотите пойти в другой ресторан?"
            res["response"]["buttons"] = rest_ask_btns()
            rest["ask_info"] = True
        elif rest["ask_info"]:
            if check_tokens(["этот", "расскажи", "него", "пойдет"], req):
                res["response"][
                    "text"] = f"Более подробно об этом ресторане вы можете узнать здесь: " \
                              f"{rest['orgs'][rest['i']]['properties']['CompanyMetaData']['url']}, желаете сменить ресторан или этот вам нравится?"
                res["response"]["buttons"] = rest_ask_btns()
                rest["change_rest"] = True
                rest["ask_info"] = False
            elif check_tokens(["другой", "меняй"], req):
                rest["ask_info"] = False
                rest["i"] += 1
                restaurant(res, req, ses)
            else:
                res["response"]["text"] = "Не поняла вас..."
                res["response"]["buttons"] = ses["last_buttons"].copy()
        elif rest["change_rest"]:
            if check_tokens(["меняй", "другой"], req):
                rest["i"] += 1
                rest["change_rest"] = False
                rest["ask_info"] = False
                restaurant(res, req, ses)
            elif check_tokens(["подходит", "пойдет", "ладно"], req):
                res["response"]["text"] = "Приятного аппетита! А не хотите узнать есть ли сегодня " \
                                          "праздник, приготовить что-нибудь сами или пойти все-таки " \
                                          "в другой ресторан?"
                res["response"]["buttons"] = actions_buttons.copy()
                ses["state"] = None
                reset_smt("restaurant", ses)
            else:
                res["response"]["text"] = "Не поняла вас..."
                res["response"]["buttons"] = ses["last_buttons"].copy()
        else:
            res["response"]["text"] = "Что-то пошло не так..."
            # по идее до сюда программа не должна доходить вообще
    except IndexError:
        res["response"]["text"] = "Кажется в вашем районе рестораны закончились, давайте что-то " \
                                  "другое, не хотите узнать какой сегодня прзадник или что " \
                                  "приготовить? "
        btns = actions_buttons.copy()
        btns.pop(2)
        res["response"]["buttons"] = btns


if __name__ == '__main__':
    app.run()
