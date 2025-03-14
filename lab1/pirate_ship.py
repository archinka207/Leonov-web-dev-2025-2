def load_ship(n, m, items):
    items.sort(key=lambda x: x[2] / x[1], reverse=True)
    
    loaded_items = []
    remaining_capacity = n
    
    for name, weight, value in items:
        if remaining_capacity == 0:
            break
        
        if weight <= remaining_capacity:
            loaded_weight = weight
            loaded_value = value
        else:
            loaded_weight = remaining_capacity
            loaded_value = (value / weight) * loaded_weight
        
        loaded_items.append((name, round(loaded_weight, 2), round(loaded_value, 2)))
        remaining_capacity -= loaded_weight
    
    for item in loaded_items:
        print(item)


n, m = map(int, input().split())
items = []
for _ in range(m):
    data = input().split()
    name, weight, value = data[0], int(data[1]), int(data[2])
    items.append((name, weight, value))

load_ship(n, m, items)