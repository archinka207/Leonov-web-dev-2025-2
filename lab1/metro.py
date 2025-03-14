n = (int)(input())
arr = []
for i in range(n):
    temp_arr = input().split()
    temp_arr = list(map(int, temp_arr))
    arr.append(temp_arr)
t = (int)(input())
ans = 0
for i in arr:
    if(t >= i[0]) and (t < i[1]):
        ans += 1

print(ans)