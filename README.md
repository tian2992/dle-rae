(D)RAE - Consulta los diccionarios de la RAE
=========================================

Fork del proyecto de Angel Carmona.

El módulo **rae** contiene las siguientes clases:
- **Article**
- **DA** (Diccionario de americanismos) *En desarrollo*
- **DEJ** (Diccionario del español jurídico) *En desarrollo*
- **DLE** (Diccionario de la lengua española)
- **DPD** (Diccionario panhispánico de dudas) *En desarrollo*

Métodos estáticos de la clase DLE
---------------------------------
- anagrams(word)
- autocomplete(substr)
- conjugate_id(verb_id)
- conjugate_verb(verb)
- contains(substring)
- ends_with(suffix)
- exact(word)
- get_lemmas()
- random_word()
- search_id(word_id)
- search_word(word, m=None)
- starts_with(prefix)
- todays_word()

---

Historial de cambios
--------------------

- 26/10/2018
-- Versión 0.0.5: Añadido install_requires en setup.py

- 25/10/2018
-- Subo el proyecto a PyPI (https://pypi.org/project/rae/) Versión 0.0.4

- 23/10/2018
-- Cambio de nombre del proyecto a RAE

- 31/08/2018
-- Expresiones regulares en vez de index() y slicing

- 30/08/2018
-- Corregido error en DLE._options()
-- Pequeñas mejoras en el código

- 24/08/2018
-- Añadidas letras mayúsculas en DLE.get_lemmas()

- 10/08/2018
-- Añadida función DLE.autocomplete()
-- filter() en vez de list comprehension
-- Creación de la clase DA

- 09/08/2018
-- Corregido otro error en DLE.get_lemmas()
-- Orden imports
-- New-style classes

- 08/08/2018
-- Corregido pequeño error en DLE.get_lemmas()

- 10/04/2018
-- Añadida compatibilidad con Python 2

- 28/11/2017
-- Borro mi cuenta de GitHub y subo el código a mi página
-- Empiezo a escribir este historial

- 27/05/2017
-- Creación de las clases _Shared, DLE, DPD y DEJ
-- Conjugación de verbos
-- Palabra aleatoria
-- Búsqueda exacta
-- Empieza por
-- Termina en
-- Contiene
-- Anagramas
-- Palabra del día
-- Listado de palabras del diccionario
-- Cambio de nombre del proyecto a pyRAE

- 05/05/2017
-- Subo la primera versión de dle-rae a GitHub. Sólo se pueden buscar las
  definiciones de una palabra
