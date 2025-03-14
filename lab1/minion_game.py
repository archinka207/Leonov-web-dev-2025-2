st = input()

glasnie = "AEIOU"
soglasnie = "BCDFGHJKLMNPQRSTVWXYZ"

score1 = 0
score2 = 0

for i in range(0, len(st)):
    if st[i] in glasnie:
        for j in range(i, len(st)):
            score1 += 1

for i in range(0, len(st)):
    if st[i] in soglasnie:
        for j in range(i, len(st)):
            score2 += 1

if score1 > score2:
    print("Кевин" + " " +(str)(score1))
else:
    print("Стюарт" + " " + (str)(score2))