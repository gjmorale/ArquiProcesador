from bs4 import BeautifulSoup
import bs4
import feedparser
import requests
import urllib
import json
import pprint
import dolphinq

def _feed_reader(feed_url):
    # feed_url % URL con el cual se obtiene el *feed*.

    fdict = feedparser.parse(feed_url)
    news_list = [] # lista con todas las noticias del *feed*.

    # nota: *fdict* es un diccionario.
    # ===== ==========================
    # print(fdict.keys()) aquí están los elementos disponibles.
    # sin embargo, los más importantes son: *feed* y *entries*.
    # - *feed*    es un diccionario de metadatos.
    # - *entries* es una lista de noticias.

    feed = fdict.feed
    print("Título:", feed.title)
    print("Descripción:", feed.description)
    # ahora, desde cada noticia del *feed*,
    # se rescata lo más importante: *link*, *title*, *date*.
    entries = fdict.entries
    for entry in entries:
        news = {}
        news['link']  = entry.id         # enlace
        news['title'] = entry.title      # título
        news['date']  = entry.published  # fecha de publicación
        news_list.append(news)

    return news_list

def _news_reader(news_url, class_keyword):
    # news_url      % URL con el cual se obtiene la noticia.
    # class_keyword % *keyword* del DOM para encontrar el cuerpo de la noticia.

    try:
        # genera una solicitud GET.
        rget = requests.get(news_url)
        soup = BeautifulSoup(rget.content, 'html.parser')
        body = soup.find('div', class_=class_keyword)
        news_content = body(['p', 'h1', 'h2'])
        return str(news_content)
    # si algo no funciona...
    except Exception as err:
        print()
        print("# #################")
        print("# Error inesperado.")
        print("# URL:", news_url)
        print("# ERR:", err)
        print()

def builder(filename):
    # filename % nombre del archivo con los *feeds*.

    # #######################################################
    # Este método busca aprovechar el diccionario subyacente,
    # que se obtiene a partir del archivo JSON.
    # Luego, sólo se debe agregar las noticias,
    # que serían los datos faltantes.
    # ###############################

    # obtiene todos los *sources* a partir del archivo.
    with open(filename) as srcfile:
        all_sources = [source for source in json.load(srcfile)]

    # herramienta para imprimir largos diccionarios.
    pp = pprint.PrettyPrinter(width=120)
    pp.pprint(all_sources)

    for source in all_sources:
        for topic in source['topic-list'][:]:
            # noticias recientes, ergo no-duplicadas.
            recent_news = []
            with open(source['id'] + '.txt') as histfile:
                all_news = histfile.read().splitlines()

            # forma el URL del *feed*.
            feed_url = source['beg-url'] + topic[0] + source['end-url']
            news_list = _feed_reader(feed_url)

            # obtiene la lista de noticias ya vistas.
            for news in news_list[:]:
                # agrega el contenido de cada noticia.
                link = news['link']
                print(link)
                # print(all_news)
                if link in all_news:
                    news_list.remove(news)
                else:
                    news['content'] = _news_reader(link, source['keyword'])
                    recent_news.append(link)
                    print(news['title'])
                # pp.pprint(all_sources)
                # input("Presione ENTER para continuar.\n")

            # agrupa el tema con la lista asociada de noticias;
            # luego, lo reemplaza por el tema que viene vacío.
            ndict = {topic[1]: news_list}
            index = source['topic-list'].index(topic)
            source['topic-list'][index] = ndict
            # pprint.pprint(source)

            # actualiza el historial de noticias ya extraídas.
            with open(source['id'] + '.txt', 'a') as histfile:
                for link in recent_news:
                    histfile.write(link + '\n')

        # elimina las llaves innecesarias.
        source.pop('id')
        source.pop('beg-url')
        source.pop('end-url')
        source.pop('keyword')
        # finalmente, encola las noticias de este *source*.
        dolphinq.enqueue(source)

# builder('RSS_sources.json')
