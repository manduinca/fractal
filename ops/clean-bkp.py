import json

file = open("bkp_05_10_db.json")
data = json.load(file)
file.close()


map = dict()
for d in data:
    if d['model'] in map:
        map[d['model']] += 1
    else:
        #print(d)
        map[d['model']] = 1

print(map)


data2 = []
logs = []
grade = []
for i, d in enumerate(data):
    if d['model'] == 'admin.logentry':
        logs.append(d)
    elif d['model'] == 'asistencia.grade':
        grade.append(d)
    elif d['model'] == 'contenttypes.contenttype':
        pass
    else:
        data2.append(d)

print(len(data))
print(len(data2))
data2 += logs[:10000] + grade[:200000]
print(len(data2))

with open("bkp_05_10_db_cleaned.json", "w") as out:
    json.dump(data2, out)
