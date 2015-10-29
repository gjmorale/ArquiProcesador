
import nltk, re, unicodedata, requests, json
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
				"Xi Jinping",
				"Nicki Minaj"])

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

def clean_word(s):
	s = rm_accents(s)
	s = s.replace(" ", "_")
	return s

def rm_http(link):
	link = link.replace("http://", "")
	link = link.replace("https://", "")
	return link

def people_filter (news):
	p_tags = []
	for person in people:
		if find_similar(news, person):
			p_tags.append(clean_word(person))
	return p_tags

def places_filter (news):
	pl_tags = []
	for pair in places.items():
		start = news.find(rm_accents(pair[0]), 0)
		while start != -1:
			#Iterate over the appearances of the place (pair[0]) and check if they are exact (exclude words like "Japanese").
			#Done by checking if next character is not alphabetic.
			if not news[start + len(pair[0])].isalpha():
				#Save value of key-value pair.
				pl_tags.append(clean_word(pair[1]))
				break
			start = news.find(rm_accents(pair[0]), start + len(pair[0]))
	return pl_tags

def events_filter (title, lang):
	#Cleans, tokenizes and lemmatizes news title to save keyowrds.
	#This way, words are saved in their dictionary form.
	#With this we have a standard way of representing an event.

	f_tags = []

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
		f_tags.append(clean_word(tok))
	return f_tags

def filter (news, title, lang):
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
	#TODO: get real url. 
	url = "http://arqui3.ing.puc.cl/dolphin_api/create_new/"
	for i in range(1,4):
		#Three chances to send a news
		try:
			r = requests.post(url, data = data)
			print (r.status_code)
			r.raise_for_status()
			break

		except requests.exceptions.RequestException:
			#General handling, for all request exceptions
			#TODO: maybe keep an error queue?
			continue
		
if __name__ == '__main__':
	#Here we recieve the dictionary from queue, filter and send each news individually.

	init_spanish_lemma_dict()

	#TODO:Add dequeue from CloudAMQP, esto por ahora no funciona.
	#d = dolphinq.dequeue()
	cont = '''Two of baseball's perennial underdogs - the Kansas City Royals and the New York Mets - will go head-to-head in this year's World Series, which starts on Tuesday.
	The Royals are appearing in their second straight Fall Classic. Last year they confounded all expectations by making the World Series, only to lose in the deciding seventh game to the San Francisco Giants.
	The team had been consistently one of the worst in baseball , and nobody had expected them to do well.
	But it has been a different story in 2015. They dominated their division - the American League Central - finishing 12 games ahead of second-placed Minnesota Twins.
	World Series Schedule
	*Start times listed are local; GMT is four hours ahead so games start at 00:00 GMT.**Games 5, 6 and 7 are only played if necessary e.g. if a team wins the first four matches, they wouldn't take place.
	Game 1 - Tuesday, October 27, 20:00 EST* - Mets @ Royals
	Game 2 - Wednesday, October 28, 20:00 EST* - Mets @ Royals
	Game 3 - Friday, October 30, 20:00 EST* - Royals @ Mets
	Game 4 - Saturday, October 31, 20:00 EST* - Royals @ Mets
	Game 5** - Sunday, November 1 - 20:00 EST* - Royals @ Mets
	Game 6** - Tuesday, November 3 - 20:00 EST* - Mets @ Royals
	Game 7** - Wednesday, November 4 - 20:00 EST* - Mets @ Royals
	On paper there is nothing small time about the New York Mets - they come from the Big Apple after all. They have never been short of resources - or celebrity fans including actor Matt Dillon, comedians Jon Stewart and Chris Rock and singer Nicki Minaj.
	But it has been their misfortune to live in the constant shadow of their neighbours across the East River, the Yankees, baseball's most glamorous and successful team, who have won the World Series no fewer than 27 times.
	The Mets were formed in 1962 to meet demand for a second Major League franchise in a city still traumatised by the controversial departure of two of its beloved teams, the New York Giants to San Francisco and the Brooklyn Dodgers to Los Angeles.
	They promptly posted the worst regular season record in modern times, and were thought of as a rather embarrassing joke. But they amazed the baseball world in 1969 by winning the World Series, being dubbed the Miracle Mets.
	Success since has been sporadic. A second World Series title followed in 1986, when, seemingly down and out against the Boston Red Sox they were handed a lifeline by the unfortunate Bill Buckner, who allowed a routine ground ball to bobble between his legs in what is arguably the most infamous error in the history of baseball.
	The Mets made the World Series again in 2000, but to underline their status as the second team in New York, they lost 4-1 to the Yankees.
	Since then there has been much hope of success, but nothing tangible, as their division - the National League East - has been dominated first by the Atlanta Braves and then the Philadelphia Phillies.
	The team have a history of signing up big-name players, only to see them under-perform.
	But success in 2015 has not been built on big-money marquee signings, but by a tight-knit roster of home-grown talent. The Mets used 26 home-grown players during the regular season, second in the majors only to San Francisco.
	Those players include all-star third baseman David Wright and utility infielder Daniel Murphy, who became the first player to hit home runs in six consecutive play-off games.
	Perhaps most remarkably, a quartet of young pitchers - Jacob deGrom, Matt Harvey, Noah Syndergaard and Steven Matz - all of whom have only ever played in the majors for the Mets - have excelled and will all feature prominently in the World Series.
	Kansas City, too, has made developing home-grown talent a priority, with the team's "farm system" widely praised as one of the finest in baseball, and responsible for stars such as first baseman Eric Hosmer, third baseman Mike Moustakas, and pitchers Kelvin Herrera and Yordano Ventura.
	It won't be a familiar name on the World Series pennant this year - but it will represent a rebuke to those who argue that only big bucks can breed sporting success.
	'''

	d = {
		"name": "British_Broadcasting_Company",
		"lang": "english",
		"topic-list": [
			{
				"/sport": [
					{
						"title": "World Series: Kansas City Royals & New York Mets aim for glory",
						"date": "26 October 2015",
						"link": "http://www.bbc.com/sport/0/baseball/34185968",
						"content": cont
					},
				]
			}
		]
	} 
	while d != None:
		#Media level
		post_content = {}

		#DB credentials
		post_content['username'] = "admin"
		post_content['password'] = "admin"

		post_content['media'] = d['name']
		lang = d['lang']

		for topic in d['topic-list']:
			#Topic level
			#Topic is a key value pair.
			post_content['category'] = list(topic.keys())[0]
			news_list = list(topic.values())[0]

			for news in news_list:
				#Here we take one news.
				post_content['title'] = news['title']
				post_content['date'] = news['date']
				post_content['nid'] = rm_http(news['link'])
				post_content['content'] = news['content']

				#Agregar tags del filtro
				post_content.update(filter(news['content'], news['title'], lang))

				http_post(post_content)

		#d = dolphinq.dequeue()
		d = None

#TODO: remove http from link
#TODO: remove accents and spaces