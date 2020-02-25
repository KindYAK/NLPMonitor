import datetime
import json

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

from elasticsearch_dsl import Search, Q

books = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)

keyword = """
    реформы | реформа
    обновленное содержание образования | обновленный содержание образование | обновлённое содержание образования | обновлённый содержание образование |
    обновленка | 
    опыт НИШ | опыта НИШ |
    НИШ | Назарабаевская интеллектуальная школа | Назарбаевская школа |
    повышение квалификации | повышение квалификация |
    лидерские курсы | лидерский курс |
    критериальное оценивание | критериальный оценивание |
    5-ти бальная система оценивания | 5 бальная система оценивания | бальная система оценивания |
    СОР | 
    СОЧ | 
    трехуровневые курсы | трёхуровневые курсы | трёхуровневый курс | трехуровневый курс |
    трехуровневые программы | трёхуровневые программы | трёхуровневый программ | трехуровневый программ |
    оценка знаний | оценка знание | 
    школьные программы | школьная программа
"""

keyword = """
Реформы в сельской школе | реформа в сельская школа |
сельская школа | сельский школа |
модернизация среднего образования | модернизация средний образование | 
цифровизация | 
интернет в сельской школе | интернет в сельский школа | 
программа ауыл ел бесiгi | программа ауыл | ел бесиги | ел бесiгi |
пилотный проект сельская школа | проект сельская школа | проект сельский школа |
ресурсный центр | 
опорная школа | опорный школа | 
ведущая школа | ведущий школа |
С дипломом в село | с дипломом в село |
мобильные школы | мобильный школа |
мобильные учителя | мобильный учитель | 
МКШ | малокомплектные школы | малокомплектная школа | малокомплектный школа
"""

q = Q(
    'bool',
    should=[Q("match_phrase", text_lemmatized=k.strip()) for k in keyword.split("|")] +
           [Q("match_phrase", text=k.strip()) for k in keyword.split("|")] +
           [Q("match_phrase", title=k.strip()) for k in keyword.split("|")],
    minimum_should_match=1
)
books = books.query(q)
books = books[:500000].scan()

output = []
for book in books:
    output.append(
        {
            "_id": book.meta.id,
            "id": book.id,
            "source": book.source,
            "author": book.author if hasattr(book, "author") else None,
            "datetime": book.datetime if hasattr(book, "datetime") else None,
            "title": book.title,
            "text": book.text,
            "url": book.url if hasattr(book, "url") else None,
            "num_views": book.num_views if hasattr(book, "num_views") else None,
        }
    )

with open("/output2.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
