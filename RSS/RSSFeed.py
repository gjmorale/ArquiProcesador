from bs4 import BeautifulSoup
import feedparser
import requests
import urllib

#This class contains all the readers of RSS


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

import requests

# fix: juntar todo el código duplicado.
#      pido perdón por este *code smell*.
# *topic* puede ser '', '/world', '/politics', entre otros.
def bbc_reader(id_start, topic):
    feed_url = "http://feeds.bbci.co.uk/news" + topic + "/rss.xml"
    fdict = feedparser.parse(feed_url)

    # nota: *fdict* es un diccionario.
    # ===== ==========================
    # print(fdict.keys()) aquí están los elementos disponibles.
    # sin embargo, los más importantes son: *feed* y *entries*.
    # - *feed* es un diccionario de metadatos.
    # - *entries* es una lista de noticias.

    new_id = id_start
    news = {} # diccionario donde se almacenarán las noticias.
    feed = fdict.feed
    print("Título:", feed.title)
    print("Descripción:", feed.description)

    entries = fdict.entries
    for entry in entries:
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
            story_body = soup.find('div', class_='story-body')
            article_text = story_body(['p', 'h1', 'h2'])
            news[new_id] = {'link': link,
                            'title': title,
                            'pubDate': pub_date,
                            'content': article_text}
        except:
            print('Error Inesperado')

        new_id += 1
    # print(news)
    return news

# bbc_reader(0, '')

# the guardian.
# *topic* puede ser '', '/football', '/football/liverpool', entre otros.
def tgd_reader(id_start, topic):
    feed_url = "http://www.theguardian.com" + topic + "/rss"
    fdict = feedparser.parse(feed_url)

    # nota: *fdict* es un diccionario.
    # ===== ==========================
    # print(fdict.keys()) aquí están los elementos disponibles.
    # sin embargo, los más importantes son: *feed* y *entries*.
    # - *feed* es un diccionario de metadatos.
    # - *entries* es una lista de noticias.

    new_id = id_start
    news = {} # diccionario donde se almacenarán las noticias.
    feed = fdict.feed
    print("Título:", feed.title)
    print("Descripción:", feed.description)

    entries = fdict.entries
    for entry in entries:
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
            story_body = soup.find('div', class_='content__article-body')
            article_text = story_body(['p', 'h1', 'h2'])
            news[new_id] = {'link': link,
                            'title': title,
                            'pubDate': pub_date,
                            'content': article_text}
            print(news)
        except:
            print('Error Inesperado')

        new_id += 1
    # print(news)
    return news

# tgd_reader(0, '/football/liverpool')
