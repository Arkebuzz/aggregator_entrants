import sqlite3

PATH_DB = 'data.db'


def _sort_dir(a: str):
    return int(a.split()[-1])


class DB:
    def __init__(self, path=PATH_DB):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.cur = self.conn.cursor()

        self.create_db()

    def create_db(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS universities(
                       name TEXT,
                       direction TEXT,
                       paid INTEGER,
                       places INTEGER,
                       temp1 INTEGER,
                       temp2 INTEGER,
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
                       all_original INTEGER,
                       cur_original INTEGER,
                       PRIMARY KEY(snils, university, paid, direction)
                       FOREIGN KEY(university, direction, paid) REFERENCES universities(name, direction, paid));
                       ''')

        self.conn.commit()

    def close(self):
        self.conn.close()

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

    def sort_by_priority_all_original(self, name):
        self.cur.execute('SELECT * FROM ranked_lists WHERE university = ? AND original <> -1 '
                         'ORDER BY bvi DESC, score DESC, paid, priority;',
                         (name,))
        abits = self.cur.fetchall()
        past = {}

        def sort_helper(st, fn):
            ab = abits[st]

            self.cur.execute('UPDATE universities SET temp1 = temp1 - 1 WHERE name = ? AND direction = ? AND paid = ?',
                             (ab[:3]))

            self.cur.execute('SELECT all_original FROM ranked_lists '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                             (*ab[:3], ab[4]))
            r_num = self.cur.fetchall()[0][0]

            self.cur.execute('UPDATE ranked_lists SET all_original = NULL '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ', (*ab[:3], ab[4]))

            for i in range(st + 1, fn):
                abit = abits[i]

                if abit[1] != ab[1] or abit[2] != ab[2]:
                    continue

                elif abit[4] not in past:
                    self.cur.execute('UPDATE ranked_lists SET all_original = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp1 = temp1 + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

                elif past[abit[4]][0] == i:
                    r_num += 1

                    self.cur.execute('UPDATE ranked_lists SET all_original = all_original - 1 '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (*abit[:3], abit[4]))

                elif past[abit[4]][1] < abit[8] and past[abit[4]][2] == abit[2] or past[abit[4]][2] == 0 and abit[
                    2] == 1:
                    continue

                elif past[abit[4]][1] > abit[8] or (past[abit[4]][2] == 1 and abit[2] == 0):
                    sort_helper(past[abit[4]][0], i)

                    self.cur.execute('UPDATE ranked_lists SET all_original = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp1 = temp1 + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

        for n, abit in enumerate(abits):
            if abit[4] in past and (past[abit[4]][1] < abit[8] and past[abit[4]][2] == abit[2] or
                                    past[abit[4]][2] == 0 and abit[2] == 1):
                continue

            self.cur.execute('SELECT places, temp1 FROM universities WHERE name = ? AND direction = ? AND paid = ?',
                             (abit[:3]))
            places, temp = self.cur.fetchall()[0]

            if places > temp:
                if abit[4] in past:
                    sort_helper(past[abit[4]][0], n)

                self.cur.execute('UPDATE universities SET temp1 = temp1 + 1 '
                                 'WHERE name = ? AND direction = ? AND paid = ?',
                                 (abit[:3]))
                self.cur.execute('UPDATE ranked_lists SET all_original = ?'
                                 'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                 (temp + 1, *abit[:3], abit[4]))

                past[abit[4]] = (n, abit[8], abit[2])

        self.conn.commit()

    def sort_by_priority_cur_original(self, name):
        self.cur.execute('SELECT * FROM ranked_lists WHERE university = ? AND original = 1 '
                         'ORDER BY bvi DESC, score DESC, paid, priority;',
                         (name,))
        abits = self.cur.fetchall()
        past = {}

        def sort_helper(st, fn):
            ab = abits[st]

            self.cur.execute('UPDATE universities SET temp2 = temp2 - 1 WHERE name = ? AND direction = ? AND paid = ?',
                             (ab[:3]))

            self.cur.execute('SELECT cur_original FROM ranked_lists '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                             (*ab[:3], ab[4]))
            r_num = self.cur.fetchall()[0][0]

            self.cur.execute('UPDATE ranked_lists SET cur_original = NULL '
                             'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ', (*ab[:3], ab[4]))

            for i in range(st + 1, fn):
                abit = abits[i]

                if abit[1] != ab[1] or abit[2] != ab[2]:
                    continue

                elif abit[4] not in past:
                    self.cur.execute('UPDATE ranked_lists SET cur_original = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp2 = temp2 + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

                elif past[abit[4]][0] == i:
                    r_num += 1

                    self.cur.execute('UPDATE ranked_lists SET cur_original = cur_original - 1 '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (*abit[:3], abit[4]))

                elif past[abit[4]][1] < abit[8] and past[abit[4]][2] == abit[2] or past[abit[4]][2] == 0 and abit[
                    2] == 1:
                    continue

                elif past[abit[4]][1] > abit[8] or (past[abit[4]][2] == 1 and abit[2] == 0):
                    sort_helper(past[abit[4]][0], i)

                    self.cur.execute('UPDATE ranked_lists SET cur_original = ? '
                                     'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                     (r_num, *abit[:3], abit[4]))
                    self.cur.execute('UPDATE universities SET temp2 = temp2 + 1 '
                                     'WHERE name = ? AND direction = ? AND paid = ?',
                                     (abit[:3]))
                    past[abit[4]] = (i, abit[8], abit[2])
                    break

        for n, abit in enumerate(abits):
            if abit[4] in past and (past[abit[4]][1] < abit[8] and past[abit[4]][2] == abit[2] or
                                    past[abit[4]][2] == 0 and abit[2] == 1):
                continue

            self.cur.execute('SELECT places, temp2 FROM universities WHERE name = ? AND direction = ? AND paid = ?',
                             (abit[:3]))
            places, temp = self.cur.fetchall()[0]

            if places > temp:
                if abit[4] in past:
                    sort_helper(past[abit[4]][0], n)

                self.cur.execute('UPDATE universities SET temp2 = temp2 + 1 '
                                 'WHERE name = ? AND direction = ? AND paid = ?',
                                 (abit[:3]))
                self.cur.execute('UPDATE ranked_lists SET cur_original = ?'
                                 'WHERE university = ? AND direction = ? AND paid = ? AND snils = ? ',
                                 (temp + 1, *abit[:3], abit[4]))

                past[abit[4]] = (n, abit[8], abit[2])

        self.conn.commit()

    def sort(self):
        self.analyze_original()

        self.cur.execute('SELECT DISTINCT name FROM universities')
        for university in self.cur.fetchall():
            self.sort_by_priority_all_original(university[0])
            self.sort_by_priority_cur_original(university[0])

    def get_data(self, snils, all_original=True):
        if all_original:
            self.cur.execute('SELECT university, direction, number, all_original FROM ranked_lists WHERE '
                             f'snils LIKE "%{snils}" AND all_original <> "NULL"')
        else:
            self.cur.execute('SELECT university, direction, number, cur_original FROM ranked_lists WHERE '
                             f'snils LIKE "%{snils}" AND cur_original <> "NULL"')

        return self.cur.fetchall()

    def get_prohodnoy(self, all_original=True):
        if all_original:
            self.cur.execute('SELECT university, direction, min(score) + 1 FROM ranked_lists '
                             'WHERE all_original <> "NULL" AND paid = 0 AND bvi = 0 GROUP BY direction ORDER BY score')
            balls = self.cur.fetchall()

            self.cur.execute('SELECT name, direction, places > temp1 FROM universities WHERE paid = 0')
            directs = {i[:2]: i[2] for i in self.cur.fetchall()}
        else:
            self.cur.execute('SELECT university, direction, min(score) + 1 FROM ranked_lists '
                             'WHERE cur_original <> "NULL" AND paid = 0 AND bvi = 0 GROUP BY direction ORDER BY score')
            balls = self.cur.fetchall()

            self.cur.execute('SELECT name, direction, places > temp2 FROM universities WHERE paid = 0')
            directs = {i[:2]: i[2] for i in self.cur.fetchall()}

        res = []
        for direct in balls:
            if directs[direct[:2]]:
                res.append(f'{direct[0]}: {direct[1]} - 0')
            else:
                res.append(f'{direct[0]}: {direct[1]} - {direct[2]}')

        return sorted(res, key=_sort_dir)


if __name__ == '__main__':
    db = DB()
    # db.sort()

    print(*db.get_prohodnoy(), sep='\n')
    print('\n\n\n')
    print(*db.get_prohodnoy(False), sep='\n')
