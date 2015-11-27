from bs4 import BeautifulSoup
import bs4
import requests
import json
import dolphinq
from time import sleep

def _emol_next_page(soup, headers, news_list_url):

    # Necessary variables to iterate over emol news pages. Sometimes (don't know why) VIEWSTATEGENERATOR doesn't appear in the html.
    view_state = soup.find("input", id = "__VIEWSTATE").get("value")
    view_state_generator = "" if soup.find("input", id = "__VIEWSTATEGENERATOR") is None else soup.find("input", id = "__VIEWSTATEGENERATOR").get("value")
    previous_page = soup.find("input", id = "__PREVIOUSPAGE").get("value")
    actual_page = soup.find("input", id = "ucTodas_ucCajaTodas_PaginaActual").get("value")
    event_target_n = int(actual_page) + 1 if int(actual_page) < 5 else 4
    event_target = "ucTodas$ucCajaTodas$RepPaginacion$ctl0" + str(event_target_n) + "$Pagina"

    # Move up one page. Try three times, in case of error.
    params =    {"__VIEWSTATE": view_state,
                "__PREVIOUSPAGE": previous_page,
                "__VIEWSTATEGENERATOR": view_state_generator,
                "ucTodas$ucCajaTodas$PaginaActual": actual_page, 
                "__EVENTTARGET": event_target,
                "__EVENTARGUMENT": ""}
    return requests.post(news_list_url, data = params, headers=headers)

def _emol_save_details(list_soup, news_list, last_dict, date, topic, last_link, last_prev_link, first_link):
    # Changes in list_soup, last_dict and news_list should persist. Not en date, last_link and first_link, have to return those
    for child in list_soup.contents[0].contents:
        news = {}
        if isinstance(child, bs4.NavigableString):
            continue
        if "fecha" in child['id'].lower():
            date = str(child.string).strip()
        else:
            last_link = str(child.find("a")['href']).strip()
            if last_prev_link == last_link:
                last_dict[0][topic] = first_link
                with open("last_emol.json", 'w') as f:
                    json.dump(last_dict, f)
                return []
            news['link']  = last_link
            news['title'] = str(child.find("a").string).strip()
            news['date']  = date
            news_list.append(news)
            if first_link == last_prev_link:
                first_link = last_link
    return [date, last_link, first_link]

def _emol_news_list_reader(news_list_url, list_keyword, topic):
    # news_list_url % URL con la lista de noticias de una categoría de emol.
    
    headers = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
    news_list = []
    date = ""

    try:
        html_content = requests.get(news_list_url, headers = headers)
    except:
        print('Error Inesperado')
        return False

    # Get last fetched link
    with open("last_emol.json") as last:
        last_dict = json.load(last)
    last_prev_link = last_dict[0][topic]
    last_link = ""
    # Save first, to avoid duplicates.
    first_link = last_prev_link

    soup = BeautifulSoup(html_content.text, 'html.parser')
    list_page = soup.find("div", id = list_keyword).prettify()
    list_soup = BeautifulSoup(list_page, 'html.parser')

    # Save news from first page.
    ret_holder = _emol_save_details(list_soup, news_list, last_dict, date, topic, last_link, last_prev_link, first_link)
    # Returns an empty list if we hit a duplicate, so we return.
    if not ret_holder:
        return news_list
    date = ret_holder[0]
    last_link = ret_holder[1]
    first_link = ret_holder[2]

    for x in range(1, 3):
        # Get the news in the first 3 pages of emol.
        try:
            html_content = _emol_next_page(soup, headers, news_list_url)
        except:
            print('Error Inesperado, no se obtuvieron todas las páginas')
            return news_list

        soup = BeautifulSoup(html_content.text, 'html.parser')
        list_page = soup.find("div", id = list_keyword).prettify()
        list_soup = BeautifulSoup(list_page, 'html.parser')

        #Saves link, date and title of news in page.
        ret_holder = _emol_save_details(list_soup, news_list, last_dict, date, topic, last_link, last_prev_link, first_link)
        if not ret_holder:
            return news_list
        date = ret_holder[0]
        last_link = ret_holder[1]
        first_link = ret_holder[2]

    last_dict[0][topic] = first_link
    with open("last_emol.json", 'w') as f:
        json.dump(last_dict, f)
    return news_list

def _emol_news_reader(news_url, class_keyword):
    # news_url      % URL con el cual se obtiene la noticia.
    # class_keyword % *keyword* del DOM para encontrar el cuerpo de la noticia.

    headers = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
    try:
        # genera una solicitud GET.
        rget = requests.get(news_url, headers = headers)
        #print (rget.status_code)
        soup = BeautifulSoup(rget.content, 'html.parser')
        body = soup.find('div', class_=class_keyword)
        news_content = []
        if body.strings:
            for string in body.strings:
                news_content.append("<p>" + string + "</p>")
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
    # filename % nombre del archivo con los NoRSS list.

    # obtiene todos los *sources* a partir del archivo. Si bien ahora hay 1 NoRSS, se deja de esta manera para mantener extensibilidad.
    with open(filename) as srcfile:
        all_sources = [source for source in json.load(srcfile)]

    for source in all_sources:
        for topic in source['topic-list'][:]:
            # forma el URL del *feed*.
            feed_url = source['beg-url'] + topic + source['end-url']
            news_list = _emol_news_list_reader(feed_url, source['list-keyword'], topic)

            # agrupa el tema con la lista asociada de noticias;
            # luego, lo reemplaza por el tema que viene vacío.
            ndict = {topic: news_list}
            index = source['topic-list'].index(topic)
            source['topic-list'][index] = ndict
            for news in news_list:
                # agrega el contenido de cada noticia.
                news['content'] = _emol_news_reader(news['link'], source['keyword'])
                if news['content'] == "[]":
                    news_list.remove(news)
                # print(news['title'])
                # input("Presione ENTER para continuar.\n")

        # Check if there are no new news, to not send empty messages
        new_news = False
        for topic_dict in source['topic-list']:
            list_per_topic = topic_dict.popitem()
            if list_per_topic and list_per_topic[1]:
                new_news = True
                break

        if new_news:
            # elimina las llaves innecesarias.
            source.pop('id')
            source.pop('beg-url')
            source.pop('end-url')
            source.pop('keyword')
            source.pop('list-keyword')
            dolphinq.enqueue(source)

#builder("NoRSS_sources.json")

#print(_emol_news_list_reader("http://www.emol.com/noticias/deportes/todas.aspx", "caja_listado_noticia_todas", "/deportes"))
#print(_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/26/761046/En-Azul-Azul-solo-piensan-en-Beccacece-17-de-diciembre-seria-presentado-como-nuevo-DT-de-la-U.html", "EmolText"))
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/26/761096/Leverkusen-publica-video-del-duro-trabajo-de-recuperacion-que-realiza-Charles-Aranguiz.html", "EmolText")
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/18/759804/Programacion-revanchas-de-la-semifinales-de-la-Copa-Chile-2015.html", "EmolText")
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/25/760955/Infografia-Como-es-el-caso-de-sobornos-que-ensombrece-al-futbol-sudamericano.html", "EmolText")
