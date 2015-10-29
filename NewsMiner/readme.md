
# *Sources*

## Motivación

Para evitar el *hardcoding* de las fuentes de noticias, se implementó un archivo [JSON] (llamado `sources.json`) que guarda *metadata* de cada medio de comunicación. La siguiente tabla explica los parámetros que debe recibir cada objeto JSON.

| Nombre       | Descripción                                       |
| ------------ | ------------------------------------------------- |
| `id`         | Identificador.                                    |
| `name`       | Nombre oficial.                                   |
| `lang`       | Idioma de las noticias.                           |
| `beg-url`    | Inicio del URL.                                   |
| `end-url`    | Fin del URL.                                      |
| `keyword`    | *Keyword* para encontrar el cuerpo de la noticia. |
| `topic-list` | Lista de categorías soportadas por el RSS.        |

## Ejemplo

Por ejemplo, el medio BBC ofrece un URL para cada categoría.

`http://feeds.bbci.co.uk/news/rss.xml`<br>
`http://feeds.bbci.co.uk/news/world/rss.xml`<br>
`http://feeds.bbci.co.uk/news/business/rss.xml`<br>
`http://feeds.bbci.co.uk/news/technology/rss.xml`

Es fácil notar que lo único que cambia es la categoría, situada al medio del URL. Por lo tanto, para almacenar esta información, parece interesante construir el siguiente JSON,

```json
{
  "id":      "BBC",
  "name":    "British Broadcasting Corporation",
  "lang":    "english",
  "beg-url": "http://feeds.bbci.co.uk/news",
  "end-url": "/rss.xml",
  "keyword": "story-body",
  "topic-list": [
    "",
    "/world",
    "/technology",
    "/business",
    "/politics",
    "/health"
  ]
}
```

Siguiendo este mismo *template*, podemos describir los servicios RSS ofrecidos por el resto de los medios de comunicaciones.

[json]: https://en.wikipedia.org/wiki/JSON
