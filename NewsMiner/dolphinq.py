import json
import pika

# ###########################################################
# adaptación de: `https://www.cloudamqp.com/docs/python.html`
# sin embargo, algunas líneas innecesarias fueron eliminadas.
# ###########################################################

cfgdict = {} # diccionario de configuración.
with open('queue.cfg', 'r') as cfgfile:
    for line in cfgfile:
        key, value = line.split('=')
        cfgdict[key] = value.rstrip() # elimina los *\n*.

# fabrica el URL de conexión,
# a partir de una elegante concatenación.
url = ('amqp://' + cfgdict['username'] +
             ':' + cfgdict['password'] +
             '@' + cfgdict['hostaddr'] +
             '/' + cfgdict['username'] )
params = pika.URLParameters(url)
params.socket_timeout = 5 # en segundos.

def enqueue(message):
    # message --> mensaje en forma de diccionario.

    # abre una nueva conexión.
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    # channel.queue_declare(queue='hello')

    # debemos entregar un *string*;
    # luego, hay que serializarlo.
    body_str = json.dumps(message)
    channel.basic_publish(exchange='', routing_key='hello', body=body_str)
    print("Noticia puesta en cola.")
    conn.close()

def dequeue():
    # abre una nueva conexión.
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    # channel.queue_declare(queue='hello')

    print("Estoy esperando nuevas noticias...")
    def callback(channel, method, properties, body):
        # convierte de *bytes* a *string*.
        body_str = body.decode('utf-8')
        # convierte de *string* a *dict*.
        news_dict = json.loads(body_str)
        # print(type(news_dict))
        print(news_dict)

    channel.basic_consume(callback, queue='hello', no_ack=True)
    channel.start_consuming() # Ctrl+C para interrumpir.
