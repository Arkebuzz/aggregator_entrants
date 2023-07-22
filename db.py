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
                       paid INTEGER,
                       places INTEGER,
                       temp INTEGER,
                       PRIMARY KEY(name, direction, paid));
                       ''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS ranked_lists(
                       university TEXT,
                       direction TEXT,
                       paid INTEGER,
                       number INTEGER,
                       snils TEXT,
                       score INTEGER,
                       bvi INTEGER,
                       original INTEGER,
                       priority INTEGER,
                       really_number INTEGER,
                       PRIMARY KEY(snils, university, paid, direction)
                       FOREIGN KEY(university, direction, paid) REFERENCES universities(name, direction, paid));
                       ''')

        self.conn.commit()

    def get_data(self, snils):
        self.cur.execute('SELECT university, direction, number, really_number FROM ranked_lists WHERE ' 
                         f'snils LIKE "%{snils}"')

        return self.cur.fetchall()

    def new_ranked_lists(self, data):
        self.cur.executemany('INSERT OR REPLACE INTO ranked_lists VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)', data)
        self.conn.commit()

    def new_university(self, data):
        self.cur.executemany('INSERT OR REPLACE INTO universities VALUES(?, ?, ?, ?, 0)', data)
        self.conn.commit()

    def analyze_original(self):
        self.cur.execute('SELECT DISTINCT snils, university FROM ranked_lists WHERE original = 1 AND snils LIKE "С%"')
        data = self.cur.fetchall()
        self.cur.executemany('UPDATE ranked_lists SET original = -1 WHERE snils = ? AND university <> ?', data)

        self.conn.commit()

    def sort_by_priority(self, name):
        self.cur.execute('SELECT * FROM ranked_lists WHERE university = ? AND original <> -1 '
                         'ORDER BY bvi DESC, score DESC, paid, priority;',
                         (name,))
        abits = self.cur.fetchall()
        past = {}

        def sort_helper(st, fn):
            ab = abits[st]

            self.cur.execute('UPDATE universities SET temp = temp - 1 WHERE name = ? AND direction = ? AND paid = ?',
                             (ab[:3]))

            self.cur.execute('SELECT really_number FROM ranked_lists '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                             (*ab[:3], ab[4]))
            r_num = self.cur.fetchall()[0][0]

            self.cur.execute('UPDATE ranked_lists SET really_number = NULL '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ', (*ab[:3], ab[4]))

            for i in range(st + 1, fn):
                abit = abits[i]

                if abit[1] != ab[1] or abit[2] != ab[2]:
                    continue

                elif abit[4] not in past:
                    self.cur.execute('UPDATE ranked_lists SET really_number = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp = temp + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

                elif past[abit[4]][1] == abit[8] and past[abit[4]][2] == abit[2]:
                    r_num += 1

                    self.cur.execute('UPDATE ranked_lists SET really_number = really_number - 1 '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (*abit[:3], abit[4]))

                elif past[abit[4]][1] <= abit[8] and past[abit[4]][2] == 0:
                    continue

                elif past[abit[4]][1] > abit[8] or (past[abit[4]][2] == 1 and abit[8] == 0):
                    sort_helper(past[abit[4]][0], i)

                    self.cur.execute('UPDATE ranked_lists SET really_number = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp = temp + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

        for n, abit in enumerate(abits):
            if abit[4] in past and past[abit[4]][1] <= abit[8] and past[abit[4]][2] == 0:
                continue

            self.cur.execute('SELECT places, temp FROM universities WHERE name = ? AND direction = ? AND paid = ?',
                             (abit[:3]))
            places, temp = self.cur.fetchall()[0]

            if places > temp:
                if abit[4] in past:
                    sort_helper(past[abit[4]][0], n)

                self.cur.execute('UPDATE universities SET temp = temp + 1 '
                                 'WHERE name = ? AND direction = ? AND paid = ?',
                                 (abit[:3]))
                self.cur.execute('UPDATE ranked_lists SET really_number = ?'
                                 'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                 (temp + 1, *abit[:3], abit[4]))

                past[abit[4]] = (n, abit[8], abit[2])

        self.conn.commit()

    def sort(self):
        self.analyze_original()

        self.cur.execute('SELECT DISTINCT name FROM universities')
        for university in self.cur.fetchall():
            self.sort_by_priority(university[0])


if __name__ == '__main__':
    db = DB()
    db.sort()
