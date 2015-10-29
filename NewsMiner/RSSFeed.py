from bs4 import BeautifulSoup
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
            # forma el URL del *feed*.
            feed_url = source['beg-url'] + topic + source['end-url']
            news_list = _feed_reader(feed_url)

            # agrupa el tema con la lista asociada de noticias;
            # luego, lo reemplaza por el tema que viene vacío.
            ndict = {topic: news_list}
            index = source['topic-list'].index(topic)
            source['topic-list'][index] = ndict
            for news in news_list:
                # agrega el contenido de cada noticia.
                news['content'] = _news_reader(news['link'], source['keyword'])
                print(news['title'])
                # pp.pprint(all_sources)
                # input("Presione ENTER para continuar.\n")

        # elimina las llaves innecesarias.
        source.pop('id')
        source.pop('beg-url')
        source.pop('end-url')
        source.pop('keyword')
        # finalmente, encola las noticias de este *source*.
        dolphinq.enqueue(source)

# builder('sources.json')

def la_tercera_reader():
    #This method reads news from La Tercera.

    d = feedparser.parse(('http://latercera.com/feed/' +
                        'manager?type=rss&sc=TEFURVJDRVJB&ul=1'))
    # d = feedparser.parse('http://www.latercera.com/feed/manager?type=rss&sc=TEFURVJDRVJB&citId=9&categoryId=656')
    news = {}
    print(len(d['entries']))
    for entry in d['entries']:
        link = entry['link']
        title = entry['title']
        pubDate = entry['published']
        try:
            html_content = urllib.request.urlopen(link).read()
        except:
            print('Error Inesperado')
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            category = (soup.findAll('a',
                                    {'class': 'section-title'}))[0].text
        except:
            category = "Otro"
        article_content = (soup.findAll('div',
                                {'class': 'article-center-text'}))[0]
        content = article_content.findAll('p')
        content_string = ""
        for p in content:
            content_string += str(p)
        news[link] = {'link': link,
                    'title': title,
                    'pubDate': pubDate,
                    'content': content_string,
                    'category': category}
    return news

def emol_link_reader(self, link):
    #This method reads news from Emol.

    # Formato link emol:
    # Header: http://www.emol.com/noticias/
    # Categoria: Espectaculos/
    # Fecha+Titulo: 2015/10/20/755206/ausencia-de-luke-skywalker-en-trailer-y-afiche-de-star-wars.html
    #
    # Como no es RSS no hay suscripción directa a feeds pero si existe una opción de recibir noticias al e-mail que se puede explorar
    #
    #link = 'http://www.emol.com/noticias/Espectaculos/2015/10/20/755206/ausencia-de-luke-skywalker-en-trailer-y-afiche-de-star-wars.html'

    try:
        html_content = urllib.request.urlopen(link).read()
    except:
        print('Error Inesperado')

        
    soup = BeautifulSoup(html_content, 'html.parser')

    title = (soup.find(id='cuDetalle_cuTitular_tituloNoticia')).text
    dropTitle = (soup.find(id='cuDetalle_cuTitular_bajadaNoticia')).text
    pubDate = (soup.find(id='cuDetalle_cuCreditos_fecha')).text
    try:
        category = (soup.find(id='cuDetalle_cuNavegador_txtseccion')).text
    except:
        category = "Otro"
    article_content = (soup.find(id='cuDetalle_cuTexto_textoNoticia')).text
    news[link] = {'link': link,
                'title': title,
                #'dropTitle' : dropTitle,
                'pubDate': pubDate,
                'content': article_content,
                'category': category}
    return news

#oad_sources('sources.json')
