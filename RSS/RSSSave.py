from py2neo import Graph
from py2neo import Node, authenticate, Relationship

from cassandra.cluster import Cluster

from RSSFeed import la_tercera_reader

d = la_tercera_reader(0)
print(d)
