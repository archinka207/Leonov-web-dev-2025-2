import re

def get_longest_words(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Удаляем знаки препинания и спецсимволы, заменяя их на пробелы
    words = re.findall(r'\b\w+\b', text)
    
    if not words:
        return []
    
    max_length = max(len(word) for word in words)
    longest_words = [word for word in words if len(word) == max_length]
    
    return longest_words


filename = "example.txt"
longest_words = get_longest_words(filename)
print("\n".join(longest_words))