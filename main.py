from flask import Flask, request, jsonify
import json
from flask_ngrok import run_with_ngrok
from functions import add_help_btn, check_tokens, get_location

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
            # "name": None,
            "state": None
        }
        # TODO: делать ли обращение к пользователь по имени?
        res["response"]["text"] = "С добрым утром! Вы хотите узнать какой сегодня праздник, " \
                                  "что приготовить на завтрак или, может, куда сходить поесть?"
        res["response"]["buttons"] = actions_buttons.copy()
        return
    session = sessionStorage[user_id]
    # name = session["name"]
    state = session["state"]
    if check_tokens(["помощь", "помоги"], req):
        res["response"]["text"] = "Я могу помочь тебе приготовить завтрак, " \
                                  "решить куда сходить поесть или сказать какой сегодня праздник."
        res["response"]["buttons"] = actions_buttons.copy()
    elif check_tokens(["что"], req) and check_tokens(["умеешь"], req):
        res["response"]["text"] = "Я могу сказать какой будет праздник, " \
                                  "в названную вами дату, сказать что и как вам приготовить или " \
                                  "сказать в какой ресторан вам сходить."
        res["response"]["buttons"] = actions_buttons.copy()
    elif check_tokens(["какой", "какие", "что"], req) and \
            check_tokens(["праздник", "праздники"], req):
        session["state"] = "holiday"
        holiday(res, req, session)
    elif check_tokens(["позавтракать", "поесть", "пообедать", "поужинать", "приготовить"], req) and \
            check_tokens(["что"], req):
        session["state"] = "recipe"
        recipe(res, req, session)
    elif check_tokens(["позавтракать", "поесть", "пообедать", "поужинать"], req) and \
            check_tokens(["где"], req):
        session["state"] = "restaurant"
        session["ask_location"] = True
        restaurant(res, req, session, True)
    elif state:
        if state == "holiday":
            holiday(res, req, session)
        elif state == "recipe":
            recipe(res, req, session)
        else:
            restaurant(res, req, session)
    else:
        res["response"]["text"] = "Что, не поняла?"
        res["response"]["buttons"] = session["last_buttons"]
        # TODO: сделать выход из навыка и фразу непонимания


def holiday(res, req, ses):
    # TODO: сделать функцию
    pass


def recipe(res, req, ses):
    # TODO: сделать функцию
    pass


def restaurant(res, req, ses, first=False):
    # TODO: доделать функцию
    # TODO: сделать возможность узнать геолокацию пользователя, не спрашивая напрямую
    if ses["ask_location"] and (location := get_location(req)):
        res["response"]["text"] = f"Ага, значит вы находитесь по следующему адресу: {location}"
    elif ses["ask_location"]:
        res["response"]["text"] = ("" if first else "Я вас не поняла. ") + "Где вы находитесь?"


if __name__ == '__main__':
    app.run()
