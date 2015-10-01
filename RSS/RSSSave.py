from py2neo import Graph
from py2neo import Node, authenticate, Relationship

from cassandra.cluster import Cluster

from RSSFeed import la_tercera_reader

authenticate("localhost:7474", "neo4j", "admin")
feeds = [(la_tercera_reader, "La Tercera")]

for feed in feeds:
    news = feed[0]()

    graph_media = Graph()
    media_query = ('match (n) where n.name = "' +
                str(feed[1]) + '" return n')
    media = graph_media.cypher.execute(media_query)
    media_node = media[0][0]

    #Save to Databases.
    for new_link in news.keys():
        #Neo4j Nodes.
        new = news[new_link]
        new_node = Node("New", name = new_link)
        title_node = Node("Title", name = new['title'])
        date_node = Node("Date", name = new['pubDate'])
        category_node = Node("Category", name = new['category'])

        #Neo4j Relationships.
        title_relation = Relationship(new_node, "title", title_node)
        was_created_relation = Relationship(new_node, "was_created", date_node)
        category_relation = Relationship(new_node, "category", category_node)

        media_relation = Relationship(media_node, "has_new", new_node)

        print(new_link)
        print(new['title'])
        print(new['pubDate'])

        graph_media.create(title_relation)
        graph_media.create(was_created_relation)
        graph_media.create(media_relation)
        graph_media.create(category_relation)

        cluster = Cluster()
        session = cluster.connect('rss')
        session.execute("INSERT INTO news (id, content) VALUES (%s, %s);",
                        (new_link, new['content']))
