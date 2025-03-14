def multiply_matrices(n, A, B):
    result = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    
    return result

n = int(input().strip())
A = [list(map(int, input().split())) for _ in range(n)]
B = [list(map(int, input().split())) for _ in range(n)]

result = multiply_matrices(n, A, B)

for row in result:
    print(" ".join(map(str, row)))

