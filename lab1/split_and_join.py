st = input()
arr = st.split()
st_res = ""
for i in range(0, len(arr)):
    if i != (len(arr) - 1):
        st_res += arr[i] + "-"
    else:
        st_res += arr[i]
print(st_res)