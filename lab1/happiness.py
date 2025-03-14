def calculate_mood(n, m, arr, set_a, set_b):
    mood = 0
    set_a, set_b = set(set_a), set(set_b)
    
    for num in arr:
        if num in set_a:
            mood += 1
        elif num in set_b:
            mood -= 1

    return mood


n, m = map(int, input().split())
arr = list(map(int, input().split()))
set_a = list(map(int, input().split()))
set_b = list(map(int, input().split()))

print(calculate_mood(n, m, arr, set_a, set_b))
