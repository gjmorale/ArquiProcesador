import sys, os
sys.path.insert(0, '../NewsMiner')
from time import sleep
import nltk, re, unicodedata, requests, json, dolphinq
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize as wt

PEOPLE = []
SP_LEMMAS = {}

#TODO: extend people and places list
PEOPLE.extend([
    "Michelle Bachelet",
    "Sebastián Dávalos",
    "Felipe Kast",
    "Jorge Burgos",
    "Barack Obama",
    "Lily Pérez",
    "Rodrigo Valdés",
    "Donald Trump",
    "Hillary Clinton",
    "Alexis Sánchez",
    "Arturo Vidal",
    "Sebastián Piñera",
    "Jorge Sampaoli",
    "Ariana Grande",
    "Ben Carson",
    "George Bush",
    "Steven Spielberg",
    "Kim Jong-un",
    "Evo Morales",
    "Patricio Walker",
    "Papa Francisco",
    "Vladimir Putin",
    "Xi Jinping",
    "Nicki Minaj"])

PLACES = {
    "Chile": "Chile",
    "Santiago": "Santiago",
    "China": "China",
    "Concepción": "Concepción",
    "Nueva York": "Nueva York",
    "New York": "Nueva York",
    "Estados Unidos": "Estados Unidos",
    "United States": "Estados Unidos",
    "EEUU": "Estados Unidos",
    "USA": "Estados Unidos",
    "Japón": "Japón",
    "Japan": "Japón",
    "Tokyo": "Tokyo",
    "Brazil": "Brazil",
    "Argentina": "Argentina",
    "Colombia": "Colombia",
    "Perú": "Perú",
    "Ecuador": "Ecuador",
    "Canada": "Canada",
    "Francia": "Francia",
    "France": "Francia",
    "Italia": "Italia",
    "Italy": "Italia",
    "Grecia": "Grecia",
    "Greece": "Grecia",
    "Vatican": "Vaticano",
    "Vaticano": "Vaticano"}

def init_spanish_lemma_dict():
    lemma_file = open("lemmatization-es.txt", mode='r', encoding="utf8")
    txt = lemma_file.read()
    txt = txt.replace("\ufeff", "")
    for pair in txt.split("\n"):
        word = pair.split("\t")[1]
        lemma = pair.split("\t")[0]
        SP_LEMMAS[word] = lemma

def find_similar(news, person):
    #Allows names to be written with a middle name or with first name abbreviated (like P. Sherman)
    palabras = [rm_accents(p) for p in person.split()]
    if len(palabras) == 2:
        if rm_accents(person) in news:
            return True
        elif person == "Papa Francisco" and "Pope Francis" in news != -1:
            #Resolver caso puntual de que al Papa se le refiere distinto en inglés y español.
            #Si hubiese más casos como este, mejor cambiar de lista a diccionario (?)
            return True
        elif palabras[0][0] + ". " + palabras[1] in news:
            return True
        elif re.search(palabras[0] +  '\s[a-zA-Z]+\.?\s' + palabras[1], news) != None:
            return True
        else:
            return False
    else:
        return person in news

def rm_accents(string):
    #Also removes tilde (~) from ñ
    if string is not None:
        return ''.join(
            c for c in unicodedata.normalize('NFD', string)
            if unicodedata.category(c) != 'Mn')
    else:
        return ""

def clean_word(string):
    string = rm_accents(string)
    string = string.replace(" ", "_")
    return string

def rm_http(link):
    link = link.replace("http://", "")
    link = link.replace("https://", "")
    return link

def people_filter(news):
    p_tags = []
    for person in PEOPLE:
        if find_similar(news, person):
            p_tags.append(clean_word(person).lower().replace(" ", "_"))
    return p_tags

def places_filter(news):
    pl_tags = []
    for pair in PLACES.items():
        start = news.lower().find(rm_accents(pair[0]).lower(), 0)
        while start != -1:
            #Iterate over the appearances of the place (pair[0]) and
            #check if they are exact (exclude words like "Japanese").
            #Done by checking if next character is not alphabetic.
            if start + len(pair[0]) >= len(news) or not news[start + len(pair[0])].isalpha():
                #Save value of key-value pair.
                pl_tags.append(clean_word(pair[1]).lower().replace(" ", "_"))
                break
            start = news.lower().find(rm_accents(pair[0]).lower(), start + len(pair[0]))
    return pl_tags

def events_filter(title, lang):
    #Cleans, tokenizes and lemmatizes news title to save keyowrds.
    #This way, words are saved in their dictionary form.
    #With this we have a standard way of representing an event.

    f_tags = []

    #Regex adapted from nltk documentation
    pattern = (
        r"(?x)"      # set flag to allow verbose regexps
        r"(?:[A-Z])(?:\.[A-Z])+\.?"  # abbreviations, e.g. U.S.A.
        r"|\w+(?:-\w+)*"            # words with optional internal hyphens
        r"|\$?\d+(?:\.\d+)?%?"      # currency and percentages, e.g. $12.40, 82%
        )

    #Tokenize title acording to the regex pattern.
    tokens = nltk.regexp_tokenize(title, pattern)

    #Remove stopwords. Lang should be either 'english' or 'spanish'.
    tokens = [w.lower() for w in tokens if w.lower() not in sw.words(lang)]

    if lang == "english":
        #Lemmatization for english.
        wnl = WordNetLemmatizer()

        #Tag words (noun, adjective, verb or adverb). Makes lemmatization more accurate.
        pos_toks = nltk.pos_tag(tokens)

        #Transform pos_tag in tag that lemmatize understand.
        wordnet_tag = {
            'NN':'n', 'NNS':'n', 'NNP':'n',
            'NNPS':'n', 'JJ':'a', 'JJR':'a',
            'JJS':'a', 'VB':'v', 'VBD':'v',
            'VBG':'v', 'VBN':'v', 'VBP':'v',
            'VBZ':'v', 'RB':'r', 'RBR':'r', 'RBS':'r'}

        #Lemmatization, with pos tags.
        for i in range(len(tokens)):
            pos_tok = pos_toks[i]
            if pos_tok[1] in wordnet_tag.keys():
                tokens[i] = wnl.lemmatize(tokens[i], wordnet_tag[pos_tok[1]])
            else:
                tokens[i] = wnl.lemmatize(tokens[i])
    elif lang == "spanish":
        #Lemmatization for spanish, using a dictionary.
        for i in range(len(tokens)):
            if tokens[i] in SP_LEMMAS.keys():
                tokens[i] = SP_LEMMAS[tokens[i]]
            #else: word not in dictionary, save token unchanged.
    for tok in tokens:
        f_tags.append(clean_word(tok))
    return f_tags

def filter(news, title, lang):
    #Applies all filters
    #Problem with some unicode characters (\u201c) (maybe??)
    tags = {}

    #Remove accents from news.
    news = rm_accents(news)

    #Apply filters
    tags['people'] = people_filter(news)
    tags['places'] = places_filter(news)
    tags['facts'] = events_filter(title, lang)
    return tags

def http_post(data):
    url = "http://arqui3.ing.puc.cl/dolphin_api/create_new/"
    for i in range(1, 4):
        #Three chances to send a news
        try:
            req = requests.post(url, data=data)
            #print (r.status_code)
            req.raise_for_status()
            break

        except requests.exceptions.RequestException:
            #General handling, for all request exceptions
            #TODO: maybe keep an error queue?
            continue

if __name__ == '__main__':
    #Here we recieve the dictionary from queue, filter and send each news individually.

    init_spanish_lemma_dict()

    while True:
        d = dolphinq.single_dequeue()
        while d != None:
            #Media level
            post_content = {}

            #DB credentials
            post_content['username'] = "admin"
            post_content['password'] = "admin"

            post_content['media'] = clean_word(d['name'])
            lang = d['lang']

            for topic in d['topic-list']:
                #Topic level
                #Topic is a key value pair.

                # If there are no news in this topic, skip it.
                if not topic:
                    continue

                post_content['category'] = clean_word(list(topic.keys())[0])
                news_list = list(topic.values())[0]

                for news in news_list:
                    #Here we take one news.
                    post_content['title'] = news['title']
                    post_content['date'] = clean_word(news['date'])
                    post_content['nid'] = rm_http(news['link'])

                    clean_content = ""
                    i = len(news['content'].split(","))
                    for token in news['content'].split(","):
                        i -= 1
                        clean_content += token
                        if clean_content[len(clean_content)-1] != ">" and i > 0:
                            clean_content += ","
                    if clean_content[0] == "[":
                        clean_content = clean_content[1:len(clean_content)]
                    if clean_content[len(clean_content)-1] == "]":
                        clean_content = clean_content[0:len(clean_content)-1]
                    post_content['content'] = clean_content

                    #Agregar tags del filtro
                    post_content.update(filter(news['content'], news['title'], lang))

                    sleep(0.5)
                    http_post(post_content)
            d = dolphinq.single_dequeue()
