import re
import sys

import pandas as pd

file = 'gost_24643.xlsx'
tables_dopusk = {
    'table1': ('Допуск прямолинейности',
               'Допуск плоскостности'),
    'table2': ('Допуск круглости',
               'Допуск цилиндричности',
               'Допуск профиля продольного сечения'),
    'table3': ('Допуск параллельности',
               'Допуск перпендикулярности',
               'Допуск наклона',
               'Допуск торцового биения',
               'Допуск полного торцового биения'),
    'table4': ('Допуск радиального биения',
               'Допуск полного радиального биения',
               'Допуск соосности',
               'Допуск симметричности',
               'Допуск пересечения осей',
               'Допуск биения в заданном направлении'),  # Delete this later
    'table5': ('Допуск радиального биения, соосности, симметричности в радиусном выражении',)  # Make to other progs
                }


def input_dopusk_type():
    dopusk_type = input('Введите цифру из списка допуска:')
    if re.match("^[0123456789]*$", dopusk_type) and 1 <= int(dopusk_type) <= 17:
        return dopusk_type
    else:
        return input_dopusk_type()


def input_size():
    size = input('Введите размер:')
    if re.match("^[.0123456789]*$", size) and int(size) > 0:
        return size
    else:
        return input_size()


def input_it():
    it = input('Введите квалитет от 1 до 16:')
    if re.match("^[0123456789]*$", it) and 1 <= int(it) <= 16:
        return it
    else:
        return input_it()


def input_accuracy():
    accuracy = input('Введите степень точности от 1 до 3:')
    if re.match("^[0123456789]*$", accuracy) and 1 <= int(accuracy) <= 3:
        return accuracy
    else:
        return input_accuracy()


def search_dopusk():
    number = 1
    menu = {}
    print_name = {}
    print('Программа расчета допусков формы и расположения')
    for k, v in tables_dopusk.items():
        for name in v:
            menu[number] = k
            print_name[number] = name
            print(f'[{number}]: {name}')
            number += 1

    dopusk_type = int(input_dopusk_type())
    size = float(input_size())
    it = int(input_it())
    accuracy = int(input_accuracy())

    try:
        with pd.ExcelFile(file) as table:
            data_frame = table.parse(menu[dopusk_type])

            for count, interval in enumerate(data_frame[data_frame.columns[0]].to_list()):
                a, b = interval.replace('от', '').replace('до', '').lstrip().split('  ')
                if int(a) < size <= int(b):

                    if it == 3 and accuracy == 3:
                        accuracy = 2
                    elif it == 2 and accuracy >= 2:
                        accuracy = 1
                    elif it == 1 and accuracy >= 1:
                        accuracy = 0

                    dopusk = data_frame.iloc[count][it - accuracy]
                    nuli = len(str(dopusk / 1000)) - 2
                    print(f'Интервал размеров: {interval} мм')
                    if it <= 12:
                        print(f'Значение допуска '
                              f'{print_name[dopusk_type][7:]}: {dopusk} мкм ({dopusk / 1000:0.{nuli}f} мм)')
                    else:
                        print(f'Значение допуска '
                              f'{print_name[dopusk_type][7:]}: {int(dopusk * 1000)} мкм ({dopusk:1.{nuli - 3}f} мм)')
                    print(f'Степень точности: {it - accuracy}')
                    break

    except FileNotFoundError:
        print('Таблицы допусков не найдены')
    except Exception:
        print('В данной таблице отсутствует запрашиваемый размер')
    question()


def question():
    print('Для повторного запуска напишите:  \'y\', для выхода: \'n\'')
    choice = input('')
    if choice == 'y':
        search_dopusk()
    elif choice == 'n':
        sys.exit()
    else:
        print('go to console')


search_dopusk()
