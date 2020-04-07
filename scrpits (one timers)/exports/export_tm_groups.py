import csv

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_TOPIC_DOCUMENT

from elasticsearch_dsl import Search

topic_groups = {
    '1': ['100', '192', '129', '4', '142', '146', '173', '36', '85', '121', '49', '151', '48', '63', '61'],
    '2': ['88', '46', '77', '57', '29', '28', '156'],
    '3': ['147', '95'],
    '4': ['37', '125', '197'],
    '5': ['114'],
    '6': ['124', '26', '47', '8', '41', '27', '188', '136'],
    '7': ['135', '31'],
    '8': ['34', '102', '78'],
    '9': ['139', '123'],
    '10': ['98'],
    '11': ['189'],
    '12': ['33', '3', '126', '40', '133'],
    '13': ['20'],
    '14': ['30', '45', '138', '79'],
    '15': ['72', '86', '143'],
    '16': ['141', '183', '131', '23', '108', '155'],
    '17': ['140', '52', '58', '81', '165', '162', '21', '185', '127', '96', '69', '141'],
    '18': ['74'],
    '19': ['105', '180', '82', '73', '160', '161'],
    '20': ['178', '110', '134'],
    '21': ['75', '188'],
    '22': ['116', '169'],
    '23': ['84', '136'],
    '24': ['136', '157', '84'],
    '25': ['80', '17'],
    '26': ['19', '68'],
    '27': ['149', '12', '16', '35', '13', '87', '117', '38', '6', '9', '159'],
    '28': ['137'],
    '29': ['164', '157', '152', '118', '195'],
    '30': ['92', '14', '128', '120'],
    '31': ['191', '190'],
    '32': ['66', '112', '144', '15', '5', '1', '195'],
    '33': ['163'],
    '34': ['177', '97'],
    '35': ['59', '53'],
    '36': ['130', '174', '145', '71'],
    '37': ['44'],
    '38': ['119', '132'],
    '39': ['25'],
    '40': ['69'],
    '41': ['89', '2', '171'],
    '42': ['56'],
    '43': ['166'],
    '44': ['18', '70'],
    '45': ['179', '153', '64', '11', '148'],
    '46': ['32', '109', '90'],
    '47': ['184', '7', '50'],
    '48': ['67', '65', '43', '115', '94', '42', '196', '122', '113', '170', '76'],
    '49': ['188', '67', '196', '122', '150'],
    '50': ['51'],
    '51': ['104', '187', '24', '187'],
    '52': ['111', '176', '199'],
    '53': ['54', '182'],
    '54': ['181'],
    '55': ['158'],
    '56': ['93'],
    '57': ['154'],
    '58': ['91'],
    '59': ['168'],
    '60': ['153']
}

tm_name = "bigartm_two_years"
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

output = []
for group_id, topics in topic_groups.items():
    news_to_export = 10
    top_news_ids = []
    for topic_id in topics:
        std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}") \
                  .filter("term", topic_id=f"topic_{topic_id}").sort('-topic_weight')[:news_to_export*2]
        top_news_ids += [{"id": r.document_es_id, "weight": r.topic_weight} for r in std.execute()]
    top_news_ids = sorted(top_news_ids, key=lambda x: x['weight'], reverse=True)[:news_to_export*3]
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)\
        .filter("terms", _id=[id['id'] for id in top_news_ids])\
        .source(('title', 'url',))
    top_news = s.execute()
    titles_seen = set()
    top_news_to_write = []
    for news in top_news:
        title = news.title.strip()
        if len(title) < 3:
            continue
        if title in titles_seen:
            continue
        top_news_to_write.append(news)
        titles_seen.add(title)
        if len(top_news_to_write) >= news_to_export:
            break
    doc = {
        "id": group_id,
    }
    # Top news
    for i in range(news_to_export):
        if i >= len(top_news_to_write):
            doc[f"top_new_{i}_title"] = ""
        else:
            doc[f"top_new_{i}_title"] = top_news_to_write[i].title
    output.append(doc)

keys = output[0].keys()
with open(f'/{tm_name}.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
