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

def _emol_news_list_reader(news_list_url):
    # news_list_url % URL con la lista de noticias de una categoría de emol.
    
    headers = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}

    try:
        html_content = requests.get(news_list_url, headers = headers)
    except:
        print('Error Inesperado')

    # Necessary variables to iterate over emol news pages.
    soup = BeautifulSoup(html_content.text, 'html.parser')
    view_state = soup.find("input", id = "__VIEWSTATE").get("value")
    view_state_generator = soup.find("input", id = "__VIEWSTATEGENERATOR").get("value")
    previous_page = soup.find("input", id = "__PREVIOUSPAGE").get("value")
    actual_page = soup.find("input", id = "ucTodas_ucCajaTodas_PaginaActual").get("value")
    event_target_n = int(actual_page) + 1 if int(actual_page) < 5 else 4
    event_target = "ucTodas$ucCajaTodas$RepPaginacion$ctl0" + event_target_n + "$Pagina"

    f = open("list.html", "w")
    f.write(soup.prettify())
    f.close()

    try:
        # Move up one page.
        params =    {"__VIEWSTATE": view_state,
                    "__PREVIOUSPAGE": previous_page,
                    "__VIEWSTATEGENERATOR": view_state_generator,
                    "ucTodas$ucCajaTodas$PaginaActual": actual_page, 
                    "__EVENTTARGET": event_target,
                    "__EVENTARGUMENT": ""}
        html_content = requests.post(news_list_url, data = params, headers=headers)
    except:
        print('Error Inesperado 2')

    soup = BeautifulSoup(html_content.text, 'html.parser')
    f = open("list2.html", "w")
    f.write(soup.prettify())
    f.close()

_emol_news_list_reader("http://www.emol.com/noticias/deportes/todas.aspx")

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
