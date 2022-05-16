import sqlite3
from typing import Union

DB = "./scores.db"


class database():
    def __init__(self) -> None:
        self.connection = sqlite3.connect(DB)
        self.cur = self.connection.cursor()

        self.check_table()

    def check_table(self) -> None:
        try:
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='top3';"
            self.cur.execute(sql)
            res = self.cur.fetchone()
            try:
                table_name = res[0]
            except TypeError:
                print("Table not found.")
                self.create_table("top3")
                print(f"Created table 'top3'.")
        except sqlite3.Error as er:
            print(f"FATAL ERROR: {er}")

    def create_table(self, name: str) -> None:
        table = f""" CREATE TABLE {name} (
            name varchar(255) not null,
            score integer not null
        ); """

        self.cur.execute(table)

    def get_top3(self) -> Union[list, str]:
        try:
            entries = []

            for i in range(3):
                if i == 0:
                    entrie = "SELECT name, MAX(score) from top3"
                    self.cur.execute(entrie)
                else:
                    if i == 2:
                        e = entries[1][0]
                    else:
                        e = " "
                    entrie = f"SELECT name, MAX(score) from top3 WHERE name NOT IN ('{entries[0][0]}', '{e}')"
                    self.cur.execute(entrie)

                entrie = self.cur.fetchone()
                entries.append(entrie)

            names = [name[0] for name in entries]
            delete = f"DELETE from top3 WHERE name NOT IN ('{names[0]}', '{names[1]}', '{names[2]}')"

            self.cur.execute(delete)
            self.connection.commit()

            return entries
        except sqlite3.Error as er:
            return str(er.args)

    def add_score(self, u_name: str, u_score: str) -> Union[list, str]:
        try:
            insert = "INSERT INTO 'top3' VALUES (?, ?)"
            self.cur.execute(insert, (u_name, u_score))
            self.connection.commit()
            return [True]
        except sqlite3.Error as er:
            return str(er.args)

    def delete(self, u_name: str) -> Union[list, str]:
        try:
            delete = f"DELETE from top3 WHERE name = '{u_name}'"
            self.cur.execute(delete)
            self.connection.commit()
            return [True]
        except sqlite3.Error as er:
            return str(er.args)


if __name__ == "__main__":
    db = database()
    entries = db.get_top3()

    print(f"1.Platz mit {entries[0][1]} Punkten: {entries[0][0]}")
    print(f"2.Platz mit {entries[1][1]} Punkten: {entries[1][0]}")
    print(f"3.Platz mit {entries[2][1]} Punkten: {entries[2][0]}")
