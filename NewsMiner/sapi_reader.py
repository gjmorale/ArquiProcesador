import requests
import json
# import pprint

PROTOCOL = 'http://'
SAPI_URL = 'arquiapi.ing.puc.cl/news'


def _unique_key(_dict):
    keylist = list(_dict.keys())
    return keylist[0]


def _get_json_content(url):
    rget = requests.get(url)
    bcontent = rget.content              # en forma de byte.
    scontent = bcontent.decode('utf-8')  # en forma de string.
    return json.loads(scontent)          # en forma de JSON.


def _get_news(news_url):
    jcontent = _get_json_content(news_url)
    news_dict = {'title':   jcontent['title'],
                 'date':    jcontent['date'],
                 'link':    jcontent['href'],
                 'content': jcontent['body']}

    # pprint.pprint(news_dict)
    return news_dict


def builder(filename, limit=10):
    with open(filename) as srcfile:
        template = json.load(srcfile)

    full_url = PROTOCOL + SAPI_URL + '?limit=' + str(limit)

    # aquí hace falta un *do-while*,
    # pero claro, Python no tiene uno. [PEP315]
    while True:
        jcontent = _get_json_content(full_url)
        news_list = jcontent['news']
        for news in news_list:
            news_dict = _get_news(PROTOCOL + news['href'])

            # busca la categoría;
            # si no existe, devuelve *None*.
            category = news['category']
            topic_list = template['topic-list']
            gen = (cat for cat in topic_list if _unique_key(cat) == category)
            cat = next(gen, None)

            if cat:
                # agrega la noticia a la categoría existente.
                key = _unique_key(cat)
                cat[key].append(news_dict)
            else:
                # agrega la nueva categoría con su noticia.
                print("Nueva categoría:", category)
                topic_list.append({category: [news_dict]})

            # input()
            # pprint.pprint(template)

        # por último, revisa si es que hay más noticias.
        next_url = jcontent['next']
        if 'page=0' not in next_url:
            full_url = PROTOCOL + next_url
        else:
            print("No hay más noticias.")
            break

builder('sapi.json')
