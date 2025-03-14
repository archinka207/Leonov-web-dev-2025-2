def second_maximum():
    n = int(input().strip())
    scores = list(map(int, input().split()))
    unique_scores = list(set(scores))
    unique_scores.sort(reverse=True)
    print(unique_scores[1])

second_maximum()