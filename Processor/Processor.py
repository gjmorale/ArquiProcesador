import re

people = []
places = []
events = []
tags = {}

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

events.extend(["terremoto",
				"concierto",
				"guerra",
				"festival",
				"batalla",
				"homicidio",
				"elección"])

def find_similar (news, person):
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

def people_filter (news):
	for person in people:
		if find_similar(news, person) != -1:
			tags[person] = "Personaje"

def places_filter (news):
	for place in places:
		if news.find(place) != -1:
			tags[place] = "Lugar"

def events_filter (news):
	#TODO: more sophisticated approach (keywords with RAKE algorithm? clustering?)
	for event in events:
		if news.find(event) != -1:
			tags[event] = "Suceso"

def filter (news):
	#Applies all filters
	people_filter(news)
	places_filter(news)
	events_filter(news)
	return tags

#test = "M. Bachelet y Barack James Obama ademas tambien homicidio de alguien en Chile o quizas China"
#print (filter(test))

#TODO: save tags to Neo4j, first should have final list of people and places and events_filter.
