def are_anagrams(s1, s2):
    return "YES" if sorted(s1) == sorted(s2) else "NO"

s1 = input().strip()
s2 = input().strip()
print(are_anagrams(s1, s2))
