import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords as sw
from nltk import word_tokenize as wt

people = []
places = []

#TODO: extend people and places list
people.extend(["Michelle Bachelet",
				"Barack Obama",
				"Lily Pérez",
				"Rodrigo Valdés",
				"Donald Trump",
				"Hillary Clinton"])

places.extend(["Chile",
				"Santiago",
				"China",
				"Concepción",
				"Nueva York",
				"Estados Unidos",
				"E.E.U.U"])

def find_similar (self, news, person):
	#Allows names to be written with a middle name or with first name abbreviated (like P. Sherman)
	palabras = person.split()
	if len(palabras) == 2:
		if news.find(person) != -1:
			return 1
		elif news.find(palabras[0][0] + ". " + palabras[1]) != -1:
			return 1
		elif re.search(palabras[0] +  '\s[a-zA-Z]+\.?\s' + palabras[1], news) != None:
			return 1
		else: 
			return -1
	else:
		return news.find(person)

def people_filter (self, news, tags):
	for person in people:
		if find_similar(news, person) != -1:
			tags[person] = "Personaje"

def places_filter (self, news, tags):
	for place in places:
		if news.find(place) != -1:
			tags[place] = "Lugar"

def events_filter (self, title, lang, tags):
	#Regex adapted from nltk documentation
	pattern = (r"(?x)"      # set flag to allow verbose regexps
	    r"(?:[A-Z])(?:\.[A-Z])+\.?"  # abbreviations, e.g. U.S.A.
	    r"|\w+(?:-\w+)*"            # words with optional internal hyphens
	    r"|\$?\d+(?:\.\d+)?%?"      # currency and percentages, e.g. $12.40, 82%
	    )

	#Tokenize title acording to the regex pattern.
	tokens = nltk.regexp_tokenize(title, pattern)

	#Remove stopwords. Lang should be either 'english' or 'spanish'.
	tokens = [w.lower() for w in tokens if w.lower() not in sw.words()] 

	#Lemmatization for english. For Spanish, just stemming (?) (TODO!!).
	wnl = WordNetLemmatizer()

	#Tag words (noun, adjective, verb or adverb). Makes lemmatization more accurate.
	pos_toks = nltk.pos_tag(tokens)
	wordnet_tag ={'NN':'n', 'NNS':'n', 'NNP':'n', 'NNPS':'n',
				'JJ':'a', 'JJR':'a', 'JJS':'a',
				'VB':'v', 'VBD':'v', 'VBG':'v', 'VBN':'v', 'VBP':'v', 'VBZ':'v',
				'RB':'r', 'RBR':'r', 'RBS':'r'}

	#Lemmatization, with pos tags.
	for i in range(len(pos_toks)):
		pos_tok = pos_toks[i]
		print (i, pos_tok)
		if pos_tok[1] in wordnet_tag.keys():
			tokens[i] = wnl.lemmatize(tokens[i], wordnet_tag[pos_tok[1]])
		else:
			tokens[i] = wnl.lemmatize(tokens[i])

def filter (self, news, lang):
	#Applies all filters
	tags = {}
	people_filter(news, tags)
	places_filter(news, tags)
	#TODO: pass title to events_filter
	#events_filter(title, lang, tags)
	return tags

#test = "M. Bachelet y Barack James Obama ademas tambien homicidio de alguien en Chile o quizas China"
#print (filter(test))

#TODO: save tags to Neo4j, first should have final list of people and places and events_filter.
