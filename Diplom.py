import re
import math
import matplotlib.pyplot as plt

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
        return f"λ={self.lam} -> n={self.n}, T={self.T}, R={self.R}"
    
def compute_RT(n2, k2, lam, d_nm, n3):
    """ Расчёт коэффициентов отражения R и пропускания T для тонкой плёнки,
    толщиной d_nm (нм), lam - длина волны в нм.
    Возвращает (R_theor, T_theor)."""

    beta = 4.0 * math.pi * k * d_nm / lam
    xi   = 4.0 * math.pi * n * d_nm / lam

    n2_sq = n2 * n2
    k2_sq = k2 * k2
    n2k2_sum = n2_sq + k2_sq
    n3_sq = n3 * n3

    A1 = (n2k2_sum + 1) * (n2k2_sum + n3_sq) - 4 * n2_sq * n3
    A2 = 2 * n2 * (n3 * (n2k2_sum + 1) - (n2k2_sum + n3_sq))
    A3 = (n2k2_sum - 1) * (n2k2_sum - n3_sq) + 4 * k2_sq * n3
    A4 = 2 * k2 * (n3 * (n2k2_sum - 1) - (n2k2_sum - n3_sq))
    A5 = (n2k2_sum + 1) * (n2k2_sum + n3_sq) + 4 * n2_sq * n3
    A6 = 2 * n2 * (n3 * (n2k2_sum + 1) + (n2k2_sum + n3_sq))
    A7 = (n2k2_sum - 1) * (n2k2_sum - n3_sq) - 4 * k2_sq * n3
    A8 = 2 * k2 * (n3 * (n2k2_sum - 1) + (n2k2_sum - n3_sq))

    ch_beta = math.cosh(beta)
    sh_beta = math.sinh(beta)
    cos_xi  = math.cos(xi)
    sin_xi  = math.sin(xi)

    denominator = (A5 * ch_beta + A6 * sh_beta - A7 * cos_xi + A8 * sin_xi)
    if abs(denominator) < 1e-12:
        return float('inf'), float('inf')

    numerator_R = A1 * ch_beta + A2 * sh_beta - A3 * cos_xi + A4 * sin_xi
    R_theor = numerator_R / denominator
    numerator_T = 8.0 * n3 * n2k2_sum
    T_theor = numerator_T / denominator
    return R_theor, T_theor


data = []
#----------------Открытие и чтение данных---------------#
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

#----------Конец блока считывания данных-------------#

#---------Параметры для подбора----------------------#
n_min, n_max = 1.0, 14.0
k_min, k_max = 0.0, 1.0
d_nm = 100.0                     # толщина плёнки

# Глобальный перебор для всех точек 
n_steps = 100
k_steps = 100

# Локальный перебор от опорной точки
delta_n = 0.1
delta_k = 0.1
n_steps_local = 100
k_steps_local = 100         

# Список для хранения лучших результатов по каждой точке
best_glob_point = []   # каждый элемент: (lam, n_sub, best_n, best_k, best_F, T_exp, R_exp, T_theor, R_theor)

print("\nВыполняется перебор для всех точек...")
for idx, row in enumerate(data):
    lam = row.lam
    n_sub = row.n
    T_exp = row.T
    R_exp = row.R

    best_n = best_k = None
    best_F = float('inf')
    best_T = best_R = None

    for i in range(n_steps):
        n = n_min + (n_max - n_min) * i / (n_steps - 1)
        for j in range(k_steps):
            k = k_min + (k_max - k_min) * j / (k_steps - 1)
            R_theor, T_theor = compute_RT(n, k, lam, d_nm, n_sub)
            F = abs(R_theor - R_exp) + abs(T_theor - T_exp)
            if F < best_F:
                best_F = F
                best_n = n
                best_k = k
                best_R = R_theor
                best_T = T_theor

    best_glob_point.append((lam, n_sub, best_n, best_k, best_F, T_exp, R_exp, best_T, best_R))

    if (idx+1) % 10 == 0 or idx == 0 or idx == len(data)-1:
        print(f"Обработано {idx+1}/{len(data)} точек. Текущая λ = {lam}")

# ---------- Поиск точки с глобальным минимумом невязки ----------
best_global = min(best_glob_point, key=lambda x: x[4])  # x[4] — это best_F

print("\n" + "="*60)
print("ОПОРНАЯ ТОЧКА С МИНИМАЛЬНОЙ НЕВЯЗКОЙ:")
print(f"Длина волны λ = {best_global[0]:.2f} нм")
print(f"Показатель преломления подложки n_sub = {best_global[1]:.4f}")
print(f"Оптимальные параметры плёнки: n_film = {best_global[2]:.6f}, k_film = {best_global[3]:.6f}")
print(f"Невязка F = {best_global[4]:.6f}")
print(f"Экспериментальные: T_exp = {best_global[5]:.6f}, R_exp = {best_global[6]:.6f}")
print(f"Теоретические:   T_theor = {best_global[7]:.6f}, R_theor = {best_global[8]:.6f}")