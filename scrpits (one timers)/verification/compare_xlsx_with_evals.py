import xlrd

from elasticsearch_dsl import Search
from sklearn.metrics import classification_report, roc_auc_score

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_DOCUMENT

tm_name = "bigartm_two_years_main_and_gos2"
criterion_id = 34

# Ground truth
document_ground_truth = dict()
xl_workbook = xlrd.open_workbook("/1.xlsx")
sheet_names = xl_workbook.sheet_names()
xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

for rownum in range(1, xl_sheet.nrows):
    try:
        document_ground_truth[str(int(xl_sheet.cell_value(rownum, 0)))] = (int(xl_sheet.cell_value(rownum, 16)) + 2) / 4
    except:
        continue

# Values
s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", id=list(document_ground_truth.keys()))
s = s.source(["id"])[:3000]
_ids_id_dict = dict(
    (d.meta.id, str(d.id)) for d in s.scan()
)
s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm_name}_{criterion_id}")
s = s.filter("terms", document_es_id=list(_ids_id_dict.keys()))
s = s.source(('value', 'document_es_id', 'id'))
document_values = dict((_ids_id_dict[d.document_es_id], d.value) for d in s.scan())

# Dataset to verify
x_y = []
for d_id in document_values:
    if d_id not in document_ground_truth:
        continue
    if document_ground_truth[d_id] not in [0.0, 1.0]:
        continue
    # if 0.4 < document_values[d_id] < 0.6:
    #     continue
    x_y.append((document_values[d_id], document_ground_truth[d_id]))

x, y = [], []
for a, b in x_y:
    x.append(bool(round(a)))
    y.append(bool(round(b)))

print(roc_auc_score(x, y))

# Verification
print(classification_report(x, y))
