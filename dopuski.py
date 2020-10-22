import re

import pandas as pd
from flask import Flask, render_template, request, session, redirect, url_for, make_response


app = Flask(__name__)


@app.errorhandler(404)
def error(err):
    return redirect(url_for('enter_page'))


@app.route('/')
def enter_page():
    table = {
        'Допуск формы': ('Допуск прямолинейности',
                         'Допуск плоскостности',
                         'Допуск круглости',
                         'Допуск цилиндричности',
                         'Допуск профиля продольного сечения'),
        'Допуск расположения': ('Допуск параллельности',
                                'Допуск перпендикулярности',
                                'Допуск наклона',
                                'Допуск соосности',
                                'Допуск симметричности',
                                'Позиционный допуск',
                                'Допуск пересечения осей'),
        'Суммарные допуски формы и расположения': ('Допуск радиального биения',
                                                   'Допуск торцового биения',
                                                   'Допуск биения в заданном направлении',
                                                   'Допуск полного радиального биения',
                                                   'Допуск полного торцового биения',
                                                   'Допуск формы заданного профиля',
                                                   'Допуск формы заданной поверхности')
        }

    image_name = {}
    count = 1
    for k, v in table.items():
        for name in v:
            image_name[name] = f'{count/100:1.2f}'.replace('.', '') + '.gif'
            count += 1

    return render_template('index.html',
                           title='Допуски формы и расположения',
                           table=table,
                           image=image_name)


@app.route('/dopusk')
def check_type():
    session['title_name'] = request.args.get('name', None)
    session['image_name'] = request.args.get('img', None)
    if session['title_name'] and session['image_name']:
        return render_template('dopusk.html',
                               title=session['title_name'],
                               image=session['image_name'])
    else:
        return redirect(url_for('enter_page'))


@app.route('/result', methods=['POST'])
def search_dopusk():
    title_name = session.get('title_name', None)
    image_name = session.get('image_name', None)

    size = request.form['size']
    if not re.match("^[.0123456789]*$", size):
        return render_template('dopusk.html',
                               title=title_name,
                               image=image_name)

    it = request.form['it']
    if not (re.match("^[0123456789]*$", it) and 1 <= int(it) <= 16):
        return render_template('dopusk.html',
                               title=title_name,
                               image=image_name)
    it = int(it)

    accuracy = int(request.form['accuracy'])

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
        'table5': ('Радиусное выражение',)  # Rename this
        }

    try:
        tablename = ''.join(k for k, v in tables_dopusk.items() if title_name in v)
        with pd.ExcelFile(file) as table:
            data_frame = table.parse(tablename)

            for count, interval in enumerate(data_frame[data_frame.columns[0]].to_list()):
                a, b = interval.replace('от', '').replace('до', '').lstrip().split('  ')
                if int(a) < float(size) <= int(b):

                    if it == 3 and accuracy == 3:
                        accuracy = 2
                    elif it == 2 and accuracy >= 2:
                        accuracy = 1
                    elif it == 1 and accuracy >= 1:
                        accuracy = 0

                    dopusk = data_frame.iloc[count][it - accuracy]  # Значение либо int64, либо float64
                    nuli = len(str(dopusk / 1000)) - 2
                    interval_razmerov = interval
                    if it <= 12:
                        dopusk_print = f'{dopusk} мкм ({dopusk / 1000:0.{nuli}f} мм)'
                    else:
                        dopusk_print = f'{int(dopusk * 1000)} мкм ({dopusk:1.{nuli - 3}f} мм)'
                    break

            return render_template('dopusk.html',
                                   title=title_name,
                                   size=size,
                                   it=it,
                                   accuracy=it - accuracy,
                                   dopusk=dopusk_print,
                                   interval_razmerov=interval_razmerov,
                                   image=image_name)
    except FileNotFoundError:
        return make_response('<h2>Таблицы допусков не найдены</h2>')
    except Exception:
        return make_response('<h2>Что-то пошло не так...</h2>')


app.secret_key = 'YouWillNeverGuessMySecretKey3'

if __name__ == '__main__':
    app.run(host='192.168.0.2', port='80', debug=True)
