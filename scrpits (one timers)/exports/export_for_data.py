import csv
import datetime
from collections import defaultdict

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT

from elasticsearch_dsl import Search

corpus = ["main", "gos2"]
tm_name = "bigartm_two_years_main_and_gos2"

group_ids = {
    'health-advice': ['topic_81', 'topic_82'],
    'animal-protection': ['topic_24', 'topic_90', 'topic_182'],
    'relationships': ['topic_105'],
    'art': ['topic_157'],
    'govermental-services': ['topic_138'],
    'war': ['topic_67', 'topic_113'],
    'stock-raising': ['topic_172'],
    'heritage': ['topic_13',
                 'topic_51',
                 'topic_84',
                 'topic_152',
                 'topic_163',
                 'topic_181'],
    'innovation-digitalization': ['topic_20', 'topic_30', 'topic_74'],
    'violent-crimes': ['topic_28',
                       'topic_37',
                       'topic_49',
                       'topic_57',
                       'topic_77',
                       'topic_88'],
    'popular-science': ['topic_64', 'topic_137', 'topic_179'],
    'diet': ['topic_82'],
    'defense': ['topic_89'],
    'business': ['topic_134', 'topic_148', 'topic_191'],
    'garbage-disposal': ['topic_180'],
    'infrastructure': ['topic_3',
                       'topic_12',
                       'topic_33',
                       'topic_53',
                       'topic_71',
                       'topic_126',
                       'topic_145'],
    'zoo': ['topic_182'],
    'kyrgyzstan': ['topic_55'],
    'cinema': ['topic_119', 'topic_132', 'topic_188'],
    'disabled-people': ['topic_22'],
    'youth': ['topic_163'],
    'fintech': ['topic_15'],
    'celebrations-holidays': ['topic_72', 'topic_143'],
    'korea': ['topic_170'],
    'migration': ['topic_47'],
    'prices': ['topic_56'],
    'agriculture': ['topic_104', 'topic_160', 'topic_172'],
    'space': ['topic_2', 'topic_76', 'topic_171'],
    'china': ['topic_193', 'topic_194'],
    'healthcare': ['topic_11', 'topic_98', 'topic_153', 'topic_175'],
    'fire': ['topic_87'],
    'energetics': ['topic_166'],
    'celebrity': ['topic_25', 'topic_121', 'topic_135'],
    'pension-system': ['topic_144'],
    'law-enforcement': ['topic_116', 'topic_197'],
    'food-recipes': ['topic_73', 'topic_161'],
    'industry': ['topic_92', 'topic_166'],
    'politics': ['topic_26',
                 'topic_52',
                 'topic_58',
                 'topic_102',
                 'topic_114',
                 'topic_124',
                 'topic_140',
                 'topic_141',
                 'topic_165',
                 'topic_167',
                 'topic_177'],
    'work': ['topic_118'],
    'weather': ['topic_19', 'topic_68'],
    'taxation': ['topic_45'],
    'education': ['topic_17', 'topic_32', 'topic_80', 'topic_93'],
    'economy': ['topic_1',
                'topic_3',
                'topic_5',
                'topic_14',
                'topic_15',
                'topic_26',
                'topic_45',
                'topic_56',
                'topic_66',
                'topic_92',
                'topic_104',
                'topic_110',
                'topic_112',
                'topic_134',
                'topic_141',
                'topic_144',
                'topic_148',
                'topic_166',
                'topic_178',
                'topic_184',
                'topic_189',
                'topic_190',
                'topic_191'],
    'language': ['topic_51', 'topic_84'],
    'railway': ['topic_145'],
    'aviation': ['topic_130'],
    'corruption': ['topic_69'],
    'employment': ['topic_184'],
    'history': ['topic_13', 'topic_18'],
    'ecology': ['topic_24', 'topic_79', 'topic_83', 'topic_180'],
    'rallies-opposition': ['topic_108', 'topic_131', 'topic_183'],
    'religion': ['topic_60', 'topic_106', 'topic_157'],
    'plane-crash': ['topic_85'],
    'tourism': ['topic_176'],
    'soviet-history': ['topic_18'],
    'appearance': ['topic_29'],
    'health': ['topic_137', 'topic_179'],
    'music': ['topic_164'],
    'criminal-trials': ['topic_46', 'topic_75', 'topic_88'],
    'coronavirus': ['topic_153', 'topic_175'],
    'urban-impovement': ['topic_33', 'topic_40', 'topic_143'],
    'mining': ['topic_14'],
    'international-politics': ['topic_8',
                               'topic_26',
                               'topic_41',
                               'topic_42',
                               'topic_43',
                               'topic_65',
                               'topic_67',
                               'topic_70',
                               'topic_78',
                               'topic_91',
                               'topic_94',
                               'topic_96',
                               'topic_113',
                               'topic_115',
                               'topic_122',
                               'topic_136',
                               'topic_142',
                               'topic_150',
                               'topic_162',
                               'topic_170',
                               'topic_193',
                               'topic_194',
                               'topic_195'],
    'housing': ['topic_59'],
    'accidents': ['topic_6',
                  'topic_28',
                  'topic_37',
                  'topic_38',
                  'topic_49',
                  'topic_77',
                  'topic_85',
                  'topic_87',
                  'topic_99',
                  'topic_125'],
    'road-accidents': ['topic_35', 'topic_125'],
    'show-business': ['topic_31', 'topic_119', 'topic_164'],
    'science-technologies': ['topic_2',
                             'topic_7',
                             'topic_20',
                             'topic_76',
                             'topic_171'],
    'parenthood': ['topic_117'],
    'countryside': ['topic_139'],
    'legislation': ['topic_114'],
    'welfare': ['topic_22', 'topic_59', 'topic_97'],
    'usa': ['topic_42', 'topic_91', 'topic_113'],
    'doping': ['topic_48'],
    'astrology-magic': ['topic_198'],
    'urban-improvement': ['topic_53', 'topic_126', 'topic_174'],
    'cars': ['topic_120'],
    'near-east': ['topic_195'],
    'congratulations': ['topic_86'],
    'public-utilities': ['topic_154'],
    'fashion': ['topic_29', 'topic_158'],
    'pets': ['topic_168'],
    'boxing': ['topic_156'],
    'banking-system': ['topic_66'],
    'cars-legislation': ['topic_128'],
    'racing': ['topic_146'],
    'sports': ['topic_4',
               'topic_48',
               'topic_63',
               'topic_99',
               'topic_100',
               'topic_129',
               'topic_146',
               'topic_156',
               'topic_192'],
    'russia': ['topic_122', 'topic_142', 'topic_199'],
    'volunteers': ['topic_155'],
    'ukraine': ['topic_162']
}

id_group = {}
for group, topic_ids in group_ids.items():
    for topic_id in topic_ids:
        id_group[topic_id] = group

# Document_topic_dict
document_group_dict = defaultdict(lambda: defaultdict(list))
document_topic_dict = defaultdict(lambda: defaultdict(int))
s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}").source(("topic_weight", "topic_id", "document_es_id"))
total = s.count()
groups = set()
for i, td in enumerate(s.scan()):
    if i % 100000 == 0:
        print(f"{i}/{total} processed")
    if td.topic_id not in id_group:
        continue
    document_group_dict[td.document_es_id][id_group[td.topic_id]].append(td.topic_weight)
    document_topic_dict[td.document_es_id][td.topic_id] = td.topic_weight
    groups.add(id_group[td.topic_id])

for key1 in document_group_dict.keys():
    for key2 in document_group_dict[key1].keys():
        try:
            document_group_dict[key1][key2] = sum(document_group_dict[key1][key2]) / len(document_group_dict[key1][key2])
        except:
            pass

groups = list(groups)
s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", corpus=corpus)
s = s.source(("text", "text_lemmatized", "title", "datetime", "url", "source", "num_views", "corpus"))
s = s.filter("range", datetime={
    "gte": datetime.date(2018, 1, 1)
})
output = []
skipped = 0
total = s.count()
for i, doc in enumerate(s.scan()):
    if i % 100_000 == 0:
        print(f"{i}/{total}")
    new_line = {
        "document_es_id": doc.meta.id,
        "text": doc.text,
        "text_lemmatized": doc.text_lemmatized if hasattr(doc, "text_lemmatized") else None,
        "title": doc.title,
        "datetime": doc.datetime if hasattr(doc, "datetime") else None,
        "url": doc.url if hasattr(doc, "url") else None,
        "source": doc.source,
        "num_views": doc.num_views if hasattr(doc, "num_views") else None,
        "type": "News" if doc.corpus == "main" else "Governmental program",
    }
    for group in groups:
        if group not in document_group_dict[doc.meta.id]:
            new_line[group] = 0
        new_line[group] = document_group_dict[doc.meta.id][group]
    for i in range(200):
        topic_id = f"topic_{i}"
        new_line[topic_id] = document_topic_dict[doc.meta.id][topic_id]
    output.append(new_line)

for group in groups:
    min_v = min([doc[group] for doc in output])
    max_v = max([doc[group] for doc in output])
    for doc in output:
        doc[group] = (doc[group] - min_v) / (max_v - min_v)

print("Skipped", skipped)

output = list(filter(lambda x: not all([(x[group] == 0 or x[group] == None) for group in groups]), output))

keys = output[0].keys()
with open(f'/output_data_social.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
