import nltk, re, unicodedata
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize as wt

people = []
sp_lemmas = {}

#TODO: extend people and places list
people.extend([	"Michelle Bachelet",
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
				"Xi Jinping"])

places =	{"Chile": "Chile",
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
	f = open("lemmatization-es.txt", mode = 'r', encoding = "utf8")
	txt = f.read()
	txt = txt.replace("\ufeff", "")
	for pair in txt.split("\n"):
		word = pair.split("\t")[1]
		lemma = pair.split("\t")[0]
		sp_lemmas[word] = lemma

def find_similar (news, person):
	#Allows names to be written with a middle name or with first name abbreviated (like P. Sherman)
	palabras = [rm_accents(p) for p in person.split()]
	if len(palabras) == 2:
		if rm_accents(person) in news:
			return True
		elif person == "Papa Francisco" and "Pope Francis" in news != -1:
			#Resolver caso puntual de que al Papa se le refiere distinto en inglés y español.
			#Si hubiese más casos como este, mejor cambiar de lista a diccionario (?)
			return True
		elif (palabras[0][0] + ". " + palabras[1]) in news:
			return True
		elif re.search(palabras[0] +  '\s[a-zA-Z]+\.?\s' + palabras[1], news) != None:
			return True
		else: 
			return False
	else:
		return person in news

def rm_accents(s):
	#Also removes tilde (~) from ñ
   	return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def people_filter (news, tags):
	for person in people:
		if find_similar(news, person):
			tags[person] = "Personaje"

def places_filter (news, tags):
	for pair in places.items():
		start = news.find(rm_accents(pair[0]), 0)
		while start != -1:
			#Iterate over the appearances of the place (pair[0]) and check if they are exact (exclude words like "Japanese").
			#Done by checking if next character is not alphabetic.
			if not news[start + len(pair[0])].isalpha():
				#Save value of key-value pair.
				tags[pair[1]] = "Lugar"
				break
			start = news.find(rm_accents(pair[0]), start + len(pair[0]))

def events_filter (title, lang, tags):
	#Cleans, tokenizes and lemmatizes news title to save keyowrds.
	#This way, words are saved in their dictionary form.
	#With this we have a standard way of representing an event.

	#Regex adapted from nltk documentation
	pattern = (r"(?x)"      # set flag to allow verbose regexps
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
		wordnet_tag ={'NN':'n', 'NNS':'n', 'NNP':'n', 'NNPS':'n',
					'JJ':'a', 'JJR':'a', 'JJS':'a',
					'VB':'v', 'VBD':'v', 'VBG':'v', 'VBN':'v', 'VBP':'v', 'VBZ':'v',
					'RB':'r', 'RBR':'r', 'RBS':'r'}

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
			if tokens[i] in sp_lemmas.keys():
				tokens[i] = sp_lemmas[tokens[i]]
			#else: word not in dictionary, save token unchanged.
	for tok in tokens:
		tags[tok] = "Suceso"

def filter (news, title, lang):
	#Applies all filters
	#Problem with some unicode characters (\u201c) (??)
	tags = {}

	#Remove accents from news.
	news = rm_accents(news)

	#Apply filters
	people_filter(news, tags)
	places_filter(news, tags)
	events_filter(title, lang, tags)
	return tags

#Working examples for spanish and english.

s = """Un tenso momento se vivió hoy en la cita que reúne todas las semanas a las directivas del bloque opositor, bautizado hace dos semanas como Chile Vamos.
	En el encuentro, los timoneles de la UDI, RN, el PRI y Evópoli discutieron sobre la elaboración del documento fundacional del conglomerado  que debe ser presentado el próximo 2 de noviembre, donde uno de los puntos que causó mayor diferencia fue la forma en que se se redactaría la posición del bloque frente al  aborto. 
	Si bien en la UDI, RN y el PRI se mantuvo una postura única, que propone como punto común la defensa de la vida del que está por nacer, la colectividad liderada por el diputado Felipe Kast marcó diferencias, las que según asistentes a la reunión, despertaron duras críticas por parte de los demás presidententes de partido. 
	Así, según indican desde la oposición, la idea de Evópoli era que el documento fundacional de Chile Vamos no hiciera alusión al aborto, dejando así una postura abierta respecto a la materia. 
	La propuesta de Kast, que se basó en la apuesta de no perder apoyos en sectores liberales de oposicón, no alcanzó consenso, y por el contrario, provocó duros cuestionamientos. 
	La presidenta del PRI, Alejandra Bravo, defendió la tesis de que el bloque debería contar con una postura cerrada en esta materia, advirtiendo que quienes no estuvieran por la búsqueda de principios comunes debiesen abandonar el bloque.
	Si nosotros tenemos una posición, que es fundamental, y alguien no está de acuerdo, mejor que no pertenezca a este bloque, afirmó. 
	Mientras el presidente de la UDI, el senador Hernán Larraín, reconoció las diferencias, advirtiendo que es propio de procesos en que las actuales coaliciones buscan ampliar sus miembros.
	El secretario general del gremialismo,  Guillermo Ramírez, agregó: Hay tres partidos de los cuatro que en su declaración de principios contemplan la proteccion de la vida desde la concepción, y hay otro partido que no lo tiene así. Yo soy de la idea de proteger la vida del que está por nacer siempre. 
	En tanto, sobre lo señalado por Felipe Kast durante el encuentro de Chile Vamos, miembros del bloque que asistieron a la reunión señalaron que éste habría reiterado su posición en contra del aborto, pero que habría advertido que resultaba un error no tener las puertas abiertas de la nueva coalición a quienes piensan distinto.
	Tras ser consultado por La Tercera, el diputado Kast optó por no referirse al tema."""

t = "Nuevo bloque opositor se divide por aborto y complica documento fundacional"

init_spanish_lemma_dict()
print (filter(s, t, "spanish"))

t = "Pope Francis 'tumour': Vatican denies 'spot on brain' report"

s = """The Vatican has rejected as "seriously irresponsible" an Italian media report that says Pope Francis has a small but curable tumour on his brain.
The Quotidiano newspaper said the Pope had travelled by helicopter to Tuscany to see a world-renowned Japanese brain surgeon.
The Pope was diagnosed with a small, dark spot but did not need surgery, the paper said.
A Vatican spokesman said the report was totally unfounded.
"As everyone can see, the Pope is carrying out his extremely intense activities in an absolutely normal manner," Father Federico Lombardi said.
Quotidiano insisted that its story was true, maintaining that the Pope had visited Prof Takanori Fukushima some months ago at the San Rossore clinic in the Barbaricina area of Pisa.
It quoted an unnamed employee at the clinic saying such a small tumour could be treated and did not need any kind of surgical intervention.
The paper's editor, Andrea Cangini, said the denial was understandable and had been expected. The timing of the report is seen as awkward for the Vatican, as 279 bishops from around the world approach the end of their three-week Synod on the Family.
The meeting, which ends on Saturday, is considered one of the key tests of Pope Francis's papacy as it has wrestled with the Church's attitude towards same-sex unions, contraception and its refusal to allow divorced and remarried Catholics to take Communion.
Earlier this year, Pope Francis, 78, indicated his papacy may last only a few years, and that he might retire like his predecessor Benedict XVI, who stepped down as pontiff in 2013.
The Pope appeared before thousands of people in St Peter's Square as normal on Wednesday, and was due to return to the Synod later in the day."""

print (filter(s, t, "english"))

#TODO: communicate with api.
#TODO: recieve news from queue.
