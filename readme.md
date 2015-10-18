# dolphin (back-end)

Este aburrido archivo `readme` habla sobre
* [descripción del componente](#descripción),
* [herramientas generales](#herramientas),
* [estructura de carpetas](#estructura),
* [manual de estilo](#manual-de-estilo).

## Descripción
Este componente de :dolphin: se puede subdividir, *grosso modo*, en **dos** fases: primero, *NewsMiner* obtiene y limpia las noticias desde las fuentes; luego, *NewsProcessor* se desarrolla un análisis sobre ellas. Entonces, para cada etapa, hemos definido un subcomponente.

### *NewsMiner*
Este subcomponente busca noticias tanto en fuentes que funcionen con RSS/Atom, como en otro tipo de noticieros —algo arcaicos, probablemente— que no ofrezcan ningún tipo de [sindicación](https://en.wikipedia.org/wiki/Web_syndication). Después de encontrar las noticias, devuelve esta información de manera organizada.

### *NewsProcessor*
Este subcomponente está encargado del procesamiento de las noticias entregadas por *NewsMiner*. Cuenta con filtros que permiten clasificar según diferentes categorías, eventos, lugares o personajes.

## Herramientas
[Python] será nuestra principal herramienta de trabajo. :snake:<br>
:warning: Para evitar fallas de compatibilidad, se **debe** usar la versión **3.4.X**.

### Librerías de Python
Las librerías utilizadas están resumidas en la siguiente tabla.

| Nombre           | ¿Y para qué?                             | Versión    |
| ---------------- | ---------------------------------------- | ----------:|
| [beautifulsoup4] | Para hacer *parsing* de documentos HTML. | **4.4.0**  |
| [feedparser]     | Para obtener noticias de fuentes RSS.    | **5.2.1**  |
| [requests]       | Para hacer solicitudes HTTP.             | **2.7.0**  |

Todas ellas aparecen en el archivo `requirements.txt`. Por lo tanto, este archivo **debe** ser usado para instalarlas con `pip`. Esto se logra con

`pip install -r requirements.txt`

En efecto, esto es... *as easy as __py__*. :grinning:

## Estructura
La estructura del repositorio está resumida en las siguientes tablas.

### Archivos

| Nombre             | ¿Y qué hace?                                            |
| ------------------ | ------------------------------------------------------- |
| `.gitignore`       | Reglas para que `git` ignore ciertos archivos/carpetas. |
| `requirements.txt` | Librerías utilizadas por `pip`.                         |

### Carpetas

| Nombre          | ¿Y qué hace?                   |
| --------------- | ------------------------------ |
| `NewsMiner`     | Minería de noticias.           |
| `NewsProcessor` | Procesamiento de las noticias. |

## Manual de estilo
Aquí no hay sorpresas: intentaremos seguir el [PEP8]. No obstante, más importante que esto, es tener en cuenta el [PEP20] —también conocido como *The Zen of Python*. El séptimo principio afirma: *readability counts*. Por esto, [Guido], nuestro benevolente pastor, nos orienta al declarar que...

> *A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is more important. Consistency within one module or function is most important.*

> *But most importantly: know when to be inconsistent — sometimes the style guide just doesn't apply. When in doubt, use your best judgment. Look at other examples and decide what looks best.*

En otras palabras, como el código será leído muchas más veces que escrito, estas reglas no deben ser aplicadas ciegamente. PEP8 nos ayuda, pero siempre debemos emplear nuestro criterio.

[python]:         http://www.pyzo.org/_images/xkcd_python.png
[beautifulsoup4]: https://pypi.python.org/pypi/beautifulsoup4
[feedparser]:     https://pypi.python.org/pypi/feedparser
[requests]:       https://pypi.python.org/pypi/requests

[pep8]:  https://www.python.org/dev/peps/pep-0008
[pep20]: https://www.python.org/dev/peps/pep-0020
[guido]: https://en.wikipedia.org/wiki/Guido_van_Rossum
