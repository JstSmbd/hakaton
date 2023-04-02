import requests
import datetime
from bs4 import BeautifulSoup as bs
from random import randint, choice


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
    except (IndexError, KeyError):
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


def rest_ask_btns(url=None):
    return [
        ({
             "title": choice(["Давай этот", "Пойдет"]),
             "hide": True
         }
         if not url else
         {
             "title": choice(["Давай этот", "Пойдет"]),
             "hide": True,
             "url": url
         }),
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
    url = 'https://www.russianfood.com/recipes/bytype/?fid=926&page='
    req = requests.get(url + str(randint(1, 44)))
    result = bs(req.content, "html.parser")
    title = result.select(".title_o > .title > a")
    variant = choice(title)
    return variant.text, 'https://www.russianfood.com' + variant.get('href')


def get_ingredients(url_recepie):
    req = requests.get(url_recepie)
    result = bs(req.content, "html.parser")
    ingredients = result.select('.ingr > tr > td > span')
    col_portions = ingredients[1].text.replace('(', '').replace(')', '')
    if 'на' in col_portions and 'порции' in col_portions:
        start = 2
    else:
        col_portions = ''
        start = 1
    for x in range(start, len(ingredients)):
        ingredients[x] = ingredients[x].text
    return col_portions, ingredients[2::]


def get_holidays(dates):  # dates - список дат по типу: ["08.03", "09.03", "10.03"]
    holidays = {'01.01': '1 января - Новый Год', '07.01': '7 января - Рождество Христово',
                '11.01': '11 января - День заповедников и национальных парков России',
                '12.01': '12 января - День работника прокуратуры Российской Федерации',
                '13.01': '13 января - День Российской печати',
                '15.01': '15 января - День образования Следственного комитета Российской федерации',
                '19.01': '19 января - Крещение Господне',
                '20.01': '20 января - День Республики Крым',
                '21.01': '21 января - День инженерных войск России',
                '25.01': '25 января - День штурмана Военно-Морского Флота России',
                '27.01': '27 января - День полного освобождения Ленинграда от фашистской блокады',
                '31.01': '31 января - Международный день ювелира',
                '01.02': '1 февраля - День работника лифтового хозяйства',
                '02.02': '2 февраля - День воинской славы России - День разгрома советскими войсками немецко-фашистских войск в Сталинградской битве',
                '07.02': '7 февраля - День российского бизнес-образования',
                '08.02': '8 февраля - День российской науки и военного топографа',
                '09.02': '9 февраля - День гражданской авиации России',
                '10.02': '10 февраля - День дипломатического работника в России',
                '14.02': '14 февраля - День Святого Валентина (день влюбленных)',
                '15.02': '15 февраля - День памяти о россиянах, исполнявших служебный долг за пределами России',
                '16.02': '16 февраля - День архива Минэнерго',
                '17.02': '17 февраля - День российских студенческих отрядов',
                '18.02': '18 февраля - День транспортной полиции России',
                '21.02': '21 февраля - Международный день родного языка',
                '23.02': '23 февраля - День защитника Отечества',
                '27.02': '27 февраля - День Сил специальных операций в России',
                '01.03': '1 марта - День эксперта-криминалиста, хостинг-провайдера в России',
                '05.03': '5 марта - День театрального кассира',
                '08.03': '8 марта - Международный женский день',
                '10.03': '10 марта - День архивов в России',
                '11.03': '11 марта - День работников геодезии, органов наркоконтроля и картографии России',
                '12.03': '12 марта - День работника уголовно-исполнительной системы России',
                '18.03': '18 марта - День воссоединения Крыма с Россией',
                '19.03': '19 марта - День моряка-подводника в России',
                '22.03': '22 марта - Всемирный день водных ресурсов',
                '23.03': '23 марта - День работников гидрометеорологической службы России',
                '24.03': '24 марта - День штурманской службы ВВС России',
                '25.03': '25 марта - День работника культуры России',
                '27.03': '27 марта - Всемирный день театра',
                '29.03': '29 марта - День специалиста юридической службы ВС России',
                '01.04': '1 апреля - День смеха (День дурака)',
                '02.04': '2 апреля - День единения народов России и Беларуси',
                '05.04': '5 апреля - День принятия Степного Уложения (Конституции) Республики Калмыкия',
                '06.04': '6 апреля - День работников следственных органов МВД России',
                '07.04': '7 апреля - День памяти погибших подводников',
                '08.04': '8 апреля - День Российской анимации, войск противовоздушной обороны и сотрудников военных комиссариатов в России',
                '11.04': '11 апреля - День конституции Республики Крым',
                '12.04': '12 апреля - День космонавтики',
                '13.04': '13 апреля - День мецената и благотворителя в России',
                '15.04': '15 апреля - День специалиста по радиоэлектронной борьбе ВС России',
                '17.04': '17 апреля - День ветеранов органов внутренних дел и внутренних войск МВД России',
                '18.04': '18 апреля - Международный день памятников и исторических мест',
                '19.04': '19 апреля - День работника ломоперерабатывающей отрасли России',
                '20.04': '20 апреля - Национальный день донора в России',
                '21.04': '21 апреля - День главного бухгалтера в России',
                '26.04': '26 апреля - День участников ликвидации последствий радиационных аварий и катастроф и памяти жертв этих аварий и катастроф',
                '27.04': '27 апреля - День российского парламентаризма',
                '28.04': '28 апреля - День работников скорой медицинской помощи',
                '30.04': '30 апреля - День пожарной охраны России',
                '01.05': '1 мая - Праздник Весны и Труда',
                '05.05': '5 мая - День водолаза, шифровальщика  в России',
                '06.05': '6 мая - День святого Георгия Победоносца',
                '07.05': '7 мая - День связиста и специалиста радиотехнической службы ВМФ России, создания вооруженных сил России',
                '08.05': '8 мая - День оперативного работника уголовно-исполнительной системы России',
                '09.05': '9 мая - День Победы',
                '13.05': '13 мая - День Черноморского флота ВМФ России',
                '14.05': '14 мая - День фрилансера в России',
                '15.05': '15 мая - Международный день семей',
                '17.05': '17 мая - Всемирный день электросвязи и информационного общества',
                '18.05': '18 мая - Международный день музеев, День Балтийского флота ВМФ России',
                '19.05': '19 мая - День ставропольского края',
                '21.05': '21 мая - День Тихоокеанского флота ВМФ России',
                '24.05': '24 мая - День кадровика в России',
                '25.05': '25 мая - День сварщика в России',
                '26.05': '26 мая - День российского предпринимательства',
                '27.05': '27 мая - Общероссийский день библиотек (День библиотекаря)',
                '28.05': '28 мая - День пограничника в России',
                '29.05': '29 мая - День ветеранов таможенной службы',
                '31.05': '31 мая - День российской адвокатуры',
                '01.06': '1 июня - Международный день защиты детей',
                '04.06': '4 июня - День крановщика', '05.06': '5 июня - День эколога',
                '06.06': '6 июня - День русского языка', '08.06': '8 июня - День Республики Карелия',
                '09.06': '9 июня - День мебельщика в России',
                '10.06': '10 июня - День работников текстильной и легкой промышленности',
                '12.06': '12 июня - День России',
                '14.06': '14 июня - День работника миграционной службы России',
                '17.06': '17 июня - День медицинского работника',
                '20.06': '20 июня - День специалиста минно-торпедной службы ВМФ России',
                '21.06': '21 июня - День кинолога',
                '22.06': '22 июня - День памяти и скорби - день начала Великой Отечественной войны',
                '23.06': '23 июня - День балалайки', '24.06': '24 июня - День Республики Чувашия',
                '27.06': '27 июня - День молодежи России',
                '29.06': '29 июня - День кораблестроителя, партизан и подпольщиков России',
                '30.06': '30 июня - День изобретателя и рационализатора, работников морского и речного флота в России',
                '01.07': '1 июля - День ветеранов боевых действий',
                '03.07': '3 июля - День ГАИ России, День образования Республики Алтай, День республики Хакасия',
                '07.07': '7 июля - День Ивана Купала',
                '08.07': '8 июля - День любви, семьи и верности',
                '11.07': '11 июля - День светооператора', '15.07': '15 июля - День Металлурга',
                '17.07': '17 июля - День основания морской авиации ВМФ России',
                '19.07': '19 июля - День юридической службы Министерства внутренних дел России',
                '24.07': '24 июля - День кадастрового инженера в России',
                '25.07': '25 июля - День сотрудника органов следствия Российской Федерации',
                '26.07': '26 июля - День парашютиста в России',
                '28.07': '28 июля - День Крещения Руси',
                '29.07': '29 июля - День Военно-Морского Флота России',
                '01.08': '1 августа - День Тыла Вооруженных Сил России, Всероссийский день инкассатора',
                '02.08': '2 августа - День Воздушно-десантных войск России',
                '05.08': '5 августа - День железнодорожника в России',
                '06.08': '6 августа - День Железнодорожных войск в России',
                '07.08': '7 августа - День Службы специальной связи и информации Федеральной службы охраны России',
                '11.08': '11 августа - День физкультурника в России',
                '12.08': '12 августа - День Военно-воздушных сил России, День строителя',
                '15.08': '15 августа - День Республики Тыва',
                '19.08': '19 августа - День Воздушного Флота России',
                '22.08': '22 августа - День Государственного флага Российской Федерации, День Республики Коми',
                '26.08': '26 августа - День шахтера в России',
                '27.08': '27 августа - День российского кино',
                '30.08': '30 августа - День Республики Татарстан',
                '01.09': '1 сентября - День знаний в России',
                '02.09': '2 сентября - День российской гвардии, работников нефтяной, газовой и топливной промышленности в России',
                '03.09': '3 сентября - День солидарности в борьбе с терроризмом',
                '04.09': '4 сентября - День специалиста по ядерному обеспечению России',
                '08.09': '8 сентября - День Новороссийского военно-морского района, День финансиста в России',
                '09.09': '9 сентября - День танкиста в России',
                '13.09': '13 сентября - День программиста в России, День парикмахера в России',
                '16.09': '16 сентября - День работников леса в России',
                '19.09': '19 сентября - День оружейника в России',
                '24.09': '24 сентября - День Государственного герба и Государственного флага республики Крым',
                '27.09': '27 сентября - День воспитателя и всех дошкольных работников в России',
                '28.09': '28 сентября - День работников атомной промышленности в России, День генерального директора в России',
                '29.09': '29 сентября - День отоларинголога',
                '30.09': '30 сентября - День машиностроителя в России',
                '01.10': '1 октября - День сухопутных войск России',
                '04.10': '4 октября - День космических войск России, День гражданской обороны МЧС России',
                '05.10': '5 октября - День учителя в России, День образования Республики Адыгея',
                '06.10': '6 октября - День российского страховщика',
                '07.10': '7 октября - День образования штабных подразделений МВД России',
                '08.10': '8 октября - День командира наводного, подводного и воздушного корабля ВМФ России',
                '11.10': '11 октября - День Республики Башкортостан',
                '14.10': '14 октября - День работника сельского хозяйства и перерабатывающей промышленности в России',
                '20.10': '20 октября - День военного связиста в России',
                '21.10': '21 октября - День работников пищевой промышленности России, День работников дорожного хозяйства в России',
                '22.10': '22 октября - День финансово-экономической службы ВС России',
                '23.10': '23 октября - День работников рекламы в России',
                '24.10': '24 октября - День подразделений специального назначения ВС России',
                '25.10': '25 октября - День работника кабельной промышленности в России',
                '27.10': '27 октября - Всероссийский день гимнастики',
                '28.10': '28 октября - День автомобилиста в России, День бабушек и дедушек',
                '29.10': '29 октября - День работников вневедомственной охраны Росгвардии',
                '30.10': '30 октября - День инженера-механика в России',
                '31.10': '31 октября - День работников СИЗО и тюрем в России',
                '01.11': '1 ноября - День судебного пристава в России',
                '04.11': '4 ноября - День народного единства',
                '05.11': '5 ноября - День военного разведчика в России',
                '07.11': '7 ноября - День Октябрьской революции 1917 года в России',
                '08.11': '8 ноября - День памяти погибших при исполнении служебных обязанностей сотрудников органов внутренних дел и военнослужащих внутренних войск МВД России',
                '10.11': '10 ноября - День сотрудника органов внутренних дел Российской Федерации',
                '11.11': '11 ноября - День экономиста в России',
                '12.11': '12 ноября - День специалиста по безопасности в России',
                '13.11': '13 ноября - День войск радиационной, химической и биологической защиты России',
                '14.11': '14 ноября - День социолога в России',
                '15.11': '15 ноября - Всероссийский день призывника',
                '17.11': '17 ноября - День участкового в России',
                '18.11': '18 ноября - День рождения Деда Мороза',
                '19.11': '19 ноября - День ракетных войск и артиллерии в России, День работника стекольной промышленности',
                '21.11': '21 ноября - День работника налоговых органов Российской федерации, День бухгалтера в России',
                '22.11': '22 ноября - День психолога в России',
                '25.11': '25 ноября - День матери в России, День российского военного миротворца',
                '27.11': '27 ноября - День морской пехоты России, День оценщика в России',
                '01.12': '1 декабря - Всемирный день борьбы со СПИДом, Всероссийский день хоккея',
                '02.12': '2 декабря - День банковского работника России, День Пермского края',
                '03.12': '3 декабря - Международный день инвалидов, День неизвестного солдата, День юриста в России',
                '07.12': '7 декабря - День инженерно-авиационной службы ВКС России',
                '09.12': '9 декабря - День Героев Отечества в России',
                '12.12': '12 декабря - День Конституции Российской Федерации',
                '15.12': '15 декабря - День памяти журналистов, погибших при исполнении профессиональных обязанностей',
                '17.12': '17 декабря - День ракетных войск стратегического назначения Вооруженных Сил России',
                '18.12': '18 декабря - День подразделений собственной безопасности органов внутренних дел России',
                '19.12': '19 декабря - День снабженца в России, День военной контрразведки в России',
                '20.12': '20 декабря - День работника органов государственной безопасности РФ',
                '22.12': '22 декабря - День энергетика в России',
                '23.12': '23 декабря - День дальней авиации ВВС России',
                '27.12': '27 декабря - День спасателя Российской Федерации'}
    hols = []
    now_lenght = 98
    for d in dates:
        try:
            dat = holidays[d]
            if len(dat) + now_lenght < 1024:
                hols.append(dat)
                now_lenght += len(dat)
            else:
                break
        except KeyError:
            pass

    return hols


def get_facts(date):  # date - дата, например, "08.03"
    # TODO: написать функцию
    return "пока не сделано"


def get_dates(req):
    command = req['request']['command']
    for symb in '.&?,!;:':
        command = command.replace(symb, '')
    dates = []
    if 'сегодня' in command:
        dates.append(datetime.datetime.now().strftime('%d.%m'))
    elif 'завтра' in command:
        dates.append((datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%d.%m'))
    elif 'следующие' in command or 'следующих' in command:
        srez = command.split(' ')
        for key in ['следующие', 'следующих']:
            if key in command:
                i = srez.index(key)
                break
        try:
            delta_days = int(srez[i - 1])
        except ValueError:
            delta_days = int(srez[i + 1])
        for x in range(0, delta_days + 1):
            dates.append((datetime.datetime.today() + datetime.timedelta(days=x)).strftime('%d.%m'))
    else:
        months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа',
                  'сентября', 'октября', 'ноября', 'декабря']
        ans = []
        for month in months:
            if month in command:
                srez = command.split()
                ans.append(months.index(month) + 1)
                i = srez.index(month)
        try:
            ans.append(int(srez[i - 1]))
        except ValueError:
            if len(srez) > i + 1:
                ans.append(int(srez[i + 1]))
            else:
                return []
        except UnboundLocalError:
            return []

        if ans[0] < 10:
            ans[0] = '0' + str(ans[0])
        else:
            ans[0] = str(ans[0])
        if ans[1] < 10:
            ans[1] = '0' + str(ans[1])
        else:
            ans[1] = str(ans[1])
        dates.append('.'.join(ans[::-1]))
    return list(dates)
