from bs4 import BeautifulSoup
import feedparser
import requests
import urllib
import json

def reader(feed_url, class_keyword):
    # feed_url      % URL con el cual se obtiene la noticia.
    # class_keyword % *keyword* del DOM para encontrar el cuerpo de la noticia.

    fdict = feedparser.parse(feed_url)

    # nota: *fdict* es un diccionario.
    # ===== ==========================
    # print(fdict.keys()) aquí están los elementos disponibles.
    # sin embargo, los más importantes son: *feed* y *entries*.
    # - *feed* es un diccionario de metadatos.
    # - *entries* es una lista de noticias.

    news = {} # diccionario donde se almacenarán las noticias.
    feed = fdict.feed
    print("Título:", feed.title)
    print("Descripción:", feed.description)

    entries = fdict.entries
    for entry in entries:
        print()
        print(entry.id)            # enlace (que será usado por *requests*)
        print(entry.title)         # título
        print(entry.summary)       # resumen
        print(entry.published)     # fecha de publicación
        # print(entry.description) # lo mismo que *summary*

        link = entry.id
        title = entry.title
        pub_date = entry.published
        try:
            r = requests.get(entry.id)
            soup = BeautifulSoup(r.content, 'html.parser')
            news_body = soup.find('div', class_=class_keyword)
            article_text = news_body(['p', 'h1', 'h2'])
            news[link] = {'link': link,
                          'title': title,
                          'pubDate': pub_date,
                          'content': article_text,
                          'category': 'None'} # categoría interina.
        except:
            print('Error inesperado.')

    # print(news)
    return news

def load_sources(filename):
    # *filename* % nombre del archivo con los *feeds*.

    with open(filename) as src_file:
        sources = json.load(src_file)
        for source in sources:
            # print(source.keys())
            for topic in source['topic-list']:
                # forma el URL del RSS.
                feed_url = source['beg-url'] + topic + source['end-url']
                # print(feed_url)
                reader(feed_url, source['keyword'])

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

load_sources('sources.json')
