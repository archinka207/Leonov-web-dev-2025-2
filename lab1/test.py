import subprocess
import pytest

INTERPRETER = 'python'

def run_script(filename, input_data=None):
    proc = subprocess.run(
        [INTERPRETER, filename],
        input='\n'.join(input_data if input_data else []),
        capture_output=True,
        text=True,
        check=False
    )
    return proc.stdout.strip()

test_data = {
    'python_if_else': [
        ('1', 'Weird'),
        ('4', 'Not Weird'),
        ('3', 'Weird'),
        ('6','Weird'),
        ('22', 'Not Weird')
    ],
    'arithmetic_operators': [
        (['1', '2'], ['3', '-1', '2']),
        (['10', '5'], ['15', '5', '50'])
    ],
    'anagram': [
        (['listen', 'silent'], 'YES'),
        (['hello', 'world'], 'NO'),
        (['triangle', 'integral'], 'YES')
    ],
    'division': [
        (['10', '2'], ['5', '5.0']),
        (['7', '3'], ['2', '2.3333333333333335']),
        (['5', '2'], ['2', '2.5']),
        (['-10', '2'], ['-5', '-5.0']),
        (['10', '-2'], ['-5', '-5.0']),
        (['0', '5'], ['0', '0.0']),
        (['5', '1'], ['5', '5.0'])
    ],
    'is_leap': [
        (['2000'], 'True'),
        (['1900'], 'False'),
        (['2004'], 'True'),
        (['2001'], 'False'),
        (['2400'], 'True')
    ],
    'lists': [
        (['5', 'append 1', 'append 2', 'append 3', 'print', 'reverse'], '[1, 2, 3]'),
        (['5', 'insert 0 5', 'insert 1 10', 'insert 0 6', 'print', 'remove 6'], '[6, 5, 10]'),
        (['5', 'append 1', 'append 2', 'append 3', 'sort', 'print'], '[1, 2, 3]'),
        (['5', 'append 1', 'append 2', 'append 3', 'pop', 'print'], '[1, 2]'),
        (['5', 'append 1', 'append 2', 'append 3', 'reverse', 'print'], '[3, 2, 1]')
    ],
    'loops': [
        ('2', '0\n1'),
        ('5', '0\n1\n4\n9\n16'),
        ('1', '0'),
        ('20', '\n'.join([str(i*i) for i in range(20)])),
    ],
    'matrix_mult': [
        (["2", "1 2", "3 4", "5 6", "7 8"], ["19 22", "43 50"]),
        (["3", "1 0 0", "0 1 0", "0 0 1", "1 2 3", "4 5 6", "7 8 9"], ["1 2 3", "4 5 6", "7 8 9"]),
        (["2", "2 3", "4 5", "6 7", "8 9"], ["36 41", "64 73"]),
        (["3", "2 1 3", "4 5 6", "7 8 9", "1 2 1", "0 1 0", "3 4 5"], ["11 17 17", "22 37 34", "34 58 52"]),
        (["2", "10 0", "0 10", "1 1", "1 1"], ["10 10", "10 10"])
    ],
    'metro' : [
        (["3", "1 5", "2 6", "4 8", "3"], ["2"]),
        (["2", "0 10", "5 15", "7"], ["2"]),
        (["4", "1 2", "3 4", "5 6", "7 8", "5"], ["1"]),
        (["3", "0 3", "2 5", "4 7", "4"], ["2"]),
        (["5", "10 20", "15 25", "20 30", "25 35", "30 40", "22"], ["2"])
    ],
    'minion_game' : [
        (["BANANA"], ["Стюарт 12"]),
        (["APPLE"], ["Стюарт 9"]),
        (["MANGO"], ["Стюарт 10"]),
        (["AEIOU"], ["Кевин 15"]),
        (["BCDFG"], ["Стюарт 15"])
    ],
    'nested_list' : [
        (["5", "Гарри", "37.21", "Берри", "37.21", "Тина", "37.2", "Акрити", "41", "Харш", "39"], ["Берри", "Гарри"]),
        (["4", "Анна", "85", "Борис", "90", "Виктор", "85", "Глеб", "95"], ["Борис"]),
        (["3", "Алиса", "78.5", "Борис", "82", "Влад", "90"], ["Борис"]),
        (["5", "Иван", "75", "Петр", "80", "Олег", "85", "Сергей", "85", "Антон", "90"], ["Петр"]),
        (["2", "Катя", "60", "Лена", "65"], ["Лена"])
    ],
    'pirate_ship' : [
        (["50 3", "Золото 30 300", "Бриллианты 20 500", "Изумруды 10 1000"], 
        ["Изумруды 10 1000", "Бриллианты 20 500", "Золото 20 200"]),
        
        (["10 2", "Сундук 5 100", "Алмазы 4 120"], 
        ["Алмазы 4.0 120.0", "Сундук 5.0 100.0"]),
        
        (["15 3", "Яблоки 10 200", "Груши 5 150", "Апельсины 3 100"], 
        ["Груши 5.0 150.0", "Яблоки 7.0 140.0", "Апельсины 3.0 100.0"])
    ],
    'print_function': [
        (['5'], '12345'),
        (['10'], '12345678910'),
        (['3'], '123'),
        (['1'], '1'),
        (['20'], '1234567891011121314151617181920')
    ],
    'second_score': [
        (['5', '2 3 6 6 5'], '5'),
        (['3', '8 10 10'], '8'),
        (['4', '1 1 2 3'], '2'),
        (['6', '1 3 2 5 5 3'], '3')
    ],
    'split_and_join': [
        (['this is a string'], 'this-is-a-string'),
        (['hello world'], 'hello-world'),
        (['python is great'], 'python-is-great'),
        (['test cases are fun'], 'test-cases-are-fun'),
        (['split and join'], 'split-and-join')
    ],
    'swap_case': [
        (['hello'], 'HELLO'),
        (['WORLD'], 'world'),
        (['PyThOn'], 'pYtHoN'),
        (['123abc'], '123ABC'),
        (['Swap CASE'], 'sWAP case')
    ]

}

def test_hello_world():
    assert run_script('hello_world.py') == 'Hello, world!'

@pytest.mark.parametrize("input_data, expected", test_data['python_if_else'])
def test_python_if_else(input_data, expected):
    assert run_script('python_if_else.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", test_data['arithmetic_operators'])
def test_arithmetic_operators(input_data, expected):
    assert run_script('arithmetic_operators.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['anagram'])
def test_anagram(input_data, expected):
    assert run_script('anagram.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['division'])
def test_division(input_data, expected):
    result = run_script('division.py', input_data).split('\n')
    assert result == expected

@pytest.mark.parametrize("input_data, expected", test_data['is_leap'])
def test_is_leap(input_data, expected):
    assert run_script('is_leap.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['lists'])
def test_lists(input_data, expected):
    assert run_script('lists.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['loops'])
def test_loops(input_data, expected):
    assert run_script('loops.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", test_data['matrix_mult'])
def test_matrix_mult(input_data, expected):
    assert run_script('matrix_mult.py', input_data).split("\n") == expected

def test_max_word():
    assert run_script('max_word.py') == 'сосредоточенности'

@pytest.mark.parametrize("input_data, expected", test_data['metro'])
def test_metro(input_data, expected):
    assert run_script('metro.py', input_data).split("\n") == expected

@pytest.mark.parametrize("input_data, expected", test_data['minion_game'])
def test_minion_game(input_data, expected):
    assert run_script('minion_game.py', input_data).split("\n") == expected

@pytest.mark.parametrize("input_data, expected", test_data['nested_list'])
def test_nested_list(input_data, expected):
    assert run_script('nested_list.py', input_data).split("\n") == expected

@pytest.mark.parametrize("input_data, expected", test_data['print_function'])
def test_print_function(input_data, expected):
    assert run_script('print_function.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['second_score'])
def test_second_score(input_data, expected):
    assert run_script('second_score.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['split_and_join'])
def test_split_and_join(input_data, expected):
    assert run_script('split_and_join.py', input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data['swap_case'])
def test_swap_case(input_data, expected):
    assert run_script('swap_case.py', input_data) == expected