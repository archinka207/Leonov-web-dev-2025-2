import csv

def calculate_expenses(filename):
    dict = {}
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Пропускаем заголовок
        
        for row in reader:
            category = row[0]
            amount = float(row[1]) + float(row[2]) + float(row[3])
            ans = category + ": " + str(amount)
            print

calculate_expenses("products.csv")