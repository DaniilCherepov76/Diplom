import re

def find_first_integer(line):
    """Возвращает первое целое число из строки или None."""
    match = re.search(r'\d+', line)
    return int(match.group()) if match else None

def parse_float(s):
    """Заменяет запятую на точку и преобразует в float."""
    return float(s.replace(',', '.'))

class SpectraRow:
    def __init__(self, lam, n, T, R):
        self.lam = lam
        self.n = n
        self.T = T
        self.R = R

    def __repr__(self):
        return f"SpectraRow(λ={self.lam}, n={self.n}, T={self.T}, R={self.R})"

data = []

try:
    with open('data.txt', 'r', encoding='utf-8') as f:
        # Читаем первую строку и извлекаем количество записей
        first_line = f.readline().strip()
        if not first_line:
            print("Ошибка: файл пуст или первая строка пустая.")
            exit()

        num_records = find_first_integer(first_line)
        if num_records is None:
            print("Ошибка: в первой строке не найдено целое число.")
            exit()

        print(f"Ожидаемое количество записей: {num_records}")

        # Читаем следующие num_records строк
        for i in range(num_records):
            line = f.readline()
            if not line:  # если файл закончился раньше
                print(f"Ошибка: файл содержит меньше {num_records} строк.")
                exit()

            line = line.strip()
            if not line:  # пропускаем пустые строки
                print(f"Предупреждение: строка {i+2} пустая, пропущена.")
                continue

            parts = line.split()
            if len(parts) != 4:
                print(f"Ошибка в строке {i+2}: ожидалось 4 числа, получено {len(parts)}.")
                exit()

            try:
                lam = parse_float(parts[0])
                n   = parse_float(parts[1])
                T   = parse_float(parts[2])
                R   = parse_float(parts[3])
                data.append(SpectraRow(lam, n, T, R))
            except ValueError as e:
                print(f"Ошибка преобразования числа в строке {i+2}: {line}")
                print(f"Детали: {e}")
                exit()

except FileNotFoundError:
    print("Ошибка: файл data.txt не найден.")
    exit()

print(f"\nУспешно прочитано {len(data)} записей.")
for i, row in enumerate(data[:5]):
    print(f"{i+1}: {row}")