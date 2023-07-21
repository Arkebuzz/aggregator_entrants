import sqlite3

PATH_DB = 'data.db'


class DB:
    def __init__(self, path=PATH_DB):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.cur = self.conn.cursor()

        self._create_db()

    def _create_db(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS universities(
                       name TEXT,
                       direction TEXT,
                       places INTEGER,
                       temp INTEGER,
                       PRIMARY KEY(name, direction));
                       ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS ranked_lists(
                       university TEXT,
                       direction TEXT,
                       number INTEGER,
                       snils TEXT,
                       score INTEGER,
                       bvi INTEGER,
                       original INTEGER,
                       priority INTEGER,
                       top_priority INTEGER,
                       really_number INTEGER,
                       PRIMARY KEY(snils, university, direction)
                       FOREIGN KEY(university, direction) REFERENCES universities(name, direction));
                       ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS entrants(
                       snils TEXT PRIMARY KEY,
                       original TEXT);
                       ''')

        self.conn.commit()

    def get_data(self, table, columns='*', orders=None, **filters):
        """

        :param table: название таблицы
        :param columns: названия нужных столбцов
        :param orders: ['column DESC/ASC']
        :param filters: столбец = значение
        :return:
        """

        if filters and orders:
            self.cur.execute(f'SELECT {columns} FROM {table} WHERE ' +
                             ' AND '.join(f'"{key}" = "{value}"' for key, value in filters.items()) +
                             f' ORDER BY {", ".join(orders)}')

        elif filters:
            self.cur.execute(f'SELECT {columns} FROM {table} WHERE ' +
                             ' AND '.join(f'"{key}" = "{value}"' for key, value in filters.items()))

        elif orders:
            self.cur.execute(f'SELECT {columns} FROM {table} ORDER BY {", ".join(orders)}')

        else:
            self.cur.execute(f'SELECT {columns} FROM {table}')

        return self.cur.fetchall()

    def delete_date(self, table, **filters):
        """

        :param table: название таблицы
        :param filters: столбец = значение
        :return:
        """

        if filters:
            self.cur.execute(f'DELETE FROM {table} WHERE ' +
                             ' AND '.join(f'"{key}" = "{value}"' for key, value in filters.items()))
        else:
            self.cur.execute(f'DELETE FROM {table}')

        self.conn.commit()

    def new_ranked_lists(self, data):
        self.cur.executemany('INSERT OR REPLACE INTO ranked_lists VALUES(?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)', data)
        self.conn.commit()

    def new_university(self, data):
        self.cur.executemany('INSERT OR REPLACE INTO universities VALUES(?, ?, ?, 0)', data)
        self.conn.commit()

    def sort_data(self, name):
        self.cur.execute('SELECT * FROM ranked_lists WHERE university = ? ORDER BY bvi DESC, score DESC, priority;',
                         (name,))
        abits = self.cur.fetchall()
        past = set()
        ln = len(abits)

        for n, abit in enumerate(abits):
            if abit[3] in past:
                continue

            self.cur.execute('SELECT places, temp FROM universities WHERE name = ? AND direction = ?', (abit[:2]))
            places, temp = self.cur.fetchall()[0]

            if places != temp:
                self.cur.execute('UPDATE universities SET temp = temp + 1 WHERE name = ? AND direction = ?',
                                 (abit[:2]))
                self.cur.execute('UPDATE ranked_lists SET really_number = ?'
                                 'WHERE university = ? AND direction = ? AND snils = ? ',
                                 (temp + 1, *abit[:2], abit[3]))

                past.add(abit[3])
                print(f'{n} / {ln}')

        self.conn.commit()


if __name__ == '__main__':
    db = DB()
    db.sort_data('МЭИ')
