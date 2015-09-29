from bs4 import BeautifulSoup
import feedparser
import urllib

#This class contains all the readers of RSS


def la_tercera_reader(idStart):
    #This method reads news from La Tercera and stores them into
    #Neo4J and Cassandra.

    d = feedparser.parse(('http://latercera.com/feed/' +
                        'manager?type=rss&sc=TEFURVJDRVJB&ul=1'))
    news = {}
    newId = idStart
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
        article_content = (soup.findAll('div',
                                {'class': 'article-center-text'}))[0]
        content = article_content.findAll('p')
        news[newId] = {'link': link,
                    'title': title,
                    'pubDate': pubDate,
                    'content': content}
        newId += 1
    return news
