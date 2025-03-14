n = (int)(input())
records = []
for i in range(0, n):
    temp_arr = []
    name = (str)(input())
    sc = (float)(input())
    temp_arr.append(name)
    temp_arr.append(sc)
    records.append(temp_arr)

scors = []
for i in range(0, n):
    scors.append(records[i][1])

scors.sort()
second_score = scors[0]

for i in range(0, n):
    if(second_score < scors[i]):
        second_score = scors[i]
        break

names = []
for i in range(0, n):
    if records[i][1] == second_score:
        names.append(records[i][0])

names.sort()
for i in names:
    print(i)