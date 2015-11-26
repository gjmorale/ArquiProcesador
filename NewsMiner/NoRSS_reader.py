from bs4 import BeautifulSoup
import bs4
import requests
import json
import pprint
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

def _emol_news_list_reader(news_list_url, list_keyword):
    # news_list_url % URL con la lista de noticias de una categoría de emol.
    
    headers = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
    news_list = []
    date = ""

    for x in range(30):
        # Sometimes the connection may fail. Try 30 times (aprox. 15 seconds) before definitely failing.
        try:
            html_content = requests.get(news_list_url, headers = headers)
        except:
            print('Error Inesperado')
            if x == 19:
                print ('No se pudo procesar emol')
                return False
            sleep(0.5)
        else:
            break

    # Get last fetched link
    with open("last_emol.txt", 'r') as f:
        last_prev_link = f.read()
    last_link = ""

    # For debugging purposes. TODO: add news link to a list.
    soup = BeautifulSoup(html_content.text, 'html.parser')
    list_page = soup.find("div", id = list_keyword).prettify()
    list_soup = BeautifulSoup(list_page, 'html.parser')

    # Save news from first page.
    for child in list_soup.contents[0].contents:
        news = {}
        if isinstance(child, bs4.NavigableString):
            continue
        if "fecha" in child['id'].lower():
            date = str(child.string).strip()
        else:
            last_link = str(child.find("a")['href']).strip()
            if last_prev_link == last_link:
                with open("last_emol.txt", 'w') as f:
                    f.write(last_link)
                return news_list
            news['link']  = last_link
            news['title'] = str(child.find("a").string).strip()
            news['date']  = date
            news_list.append(news)

    for x in range(1, 3):
        # Get the news in the first 3 pages of emol.

        got_page = False
        for y in range(3):
            # Make 3 attempts at getting the next page.
            try:
                html_content = _emol_next_page(soup, headers, news_list_url)
            except:
                print('Error Inesperado')
                sleep(0.8)
            else:
                # Correctly got page.
                got_page = True
                break

        if got_page:
            soup = BeautifulSoup(html_content.text, 'html.parser')
            list_page = soup.find("div", id = list_keyword).prettify()
            list_soup = BeautifulSoup(list_page, 'html.parser')

            for child in list_soup.contents[0].contents:
                news = {}
                if isinstance(child, bs4.NavigableString):
                    continue
                if "fecha" in child['id'].lower():
                    date = str(child.string).strip()
                else:
                    last_link = str(child.find("a")['href']).strip()
                    if last_prev_link == last_link:
                        with open("last_emol.txt", 'w') as f:
                            f.write(last_link)
                        return news_list
                    news['link']  = last_link
                    news['title'] = str(child.find("a").string).strip()
                    news['date']  = date
                    news_list.append(news)

    with open("last_emol.txt", 'w') as f:
        f.write(last_link)
    return news_list

def _emol_news_reader(news_url, class_keyword):
    # news_url      % URL con el cual se obtiene la noticia.
    # class_keyword % *keyword* del DOM para encontrar el cuerpo de la noticia.

    headers = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
    try:
        # genera una solicitud GET.
        rget = requests.get(news_url, headers = headers)
        soup = BeautifulSoup(rget.content, 'html.parser')
        body = soup.find('div', class_=class_keyword)
        news_content = ""
        for string in body.strings:
            news_content = news_content + string + "\n\n"
        return news_content
    # si algo no funciona...
    except Exception as err:
        print()
        print("# #################")
        print("# Error inesperado.")
        print("# URL:", news_url)
        print("# ERR:", err)
        print()

#print(_emol_news_list_reader("http://www.emol.com/noticias/deportes/todas.aspx", "caja_listado_noticia_todas"))
#print(_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/26/761046/En-Azul-Azul-solo-piensan-en-Beccacece-17-de-diciembre-seria-presentado-como-nuevo-DT-de-la-U.html", "EmolText"))
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/26/761096/Leverkusen-publica-video-del-duro-trabajo-de-recuperacion-que-realiza-Charles-Aranguiz.html", "EmolText")
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/18/759804/Programacion-revanchas-de-la-semifinales-de-la-Copa-Chile-2015.html", "EmolText")
#_emol_news_reader("http://www.emol.com/noticias/Deportes/2015/11/25/760955/Infografia-Como-es-el-caso-de-sobornos-que-ensombrece-al-futbol-sudamericano.html", "EmolText")
