import json


def chunks_iter(filename, chunksize=100):
    objects = []
    with open(filename, "r") as f:
        obj = ""
        for line in f:
            line = line.strip()
            obj += line
            if line == "}":
                objects.append(json.loads(obj))
                obj = ""
            if len(objects) >= chunksize:
                yield objects
                objects = []


objects = []
for chunk in chunks_iter("/scopuspubs.json", chunksize=100):
    objects.extend(chunk)
    break



